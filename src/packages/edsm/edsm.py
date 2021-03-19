from __future__ import annotations
import requests
import numpy as np
import logging
from dataclasses import dataclass
from main import config
import json

from typing import Optional
from ..datamodels.edsm_classes import SystemInfo, Coordinates, Location

class EDSMLookupError(Exception):
    """
    Base class for lookup errors
    """

class NoResultsEDSM(EDSMLookupError):
    """
    No results for the given query were found with the EDSM API
    """

class EDSMConnectionError(EDSMLookupError):
    """
    Request failed due to an exception that occurred
    while connecting to the EDSM API
    """


landmarks = []

@dataclass(frozen=True)
class GalaxySystem:
    name: str
    coords: Coordinates
    coordsLocked: bool
    information: SystemInfo

    @classmethod
    async def get_info(cls, name) -> Optional[GalaxySystem]:
        try:
            response = requests.get("https://www.edsm.net/api-v1/system",
                                    params={"systemName": name.strip(),
                                            "showCoordinates": 1,
                                            "showInformation": 1})
            responses = response.json()

        except requests.exceptions.RequestException as er:
            logging.error(f"EDSM: Error in `system get_info()` lookup: {er}", exc_info=True)
            raise EDSMConnectionError("Unable to verify system, having issues connecting to the EDSM API.")

        # Return None if system doesn't exist
        if len(responses) == 0:
            return None
        else:
            return cls(**responses)

    @classmethod
    async def exists(cls, name) -> bool:
        try:
            obj = await cls.get_info(name)
        except EDSMConnectionError:
            raise
        if obj is None:
            return False
        else:
            return True


@dataclass(frozen=True)
class Commander:
    name: str
    system: str
    coordinates: Coordinates
    date: Optional[str]
    isDocked: bool
    station: Optional[str]
    dateDocked: Optional[str]
    shipType: str
    dateLastActivity: str
    shipFuel: Optional

    @classmethod
    async def get_cmdr(cls, name) -> Optional[Commander]:
        try:
            response = requests.get("https://www.edsm.net/api-logs-v1/get-position",
                                    params={"commanderName": name,
                                            "showCoordinates": 1})
            responses = response.json()

            if responses['msgnum'] == 203:
                return None

            # Why do we have to do this? come on, EDSM!
            if not responses['isDocked']:
                responses['station'], responses['dateDocked'] = None, None

        except requests.exceptions.RequestException as er:
            logging.error(f"EDSM: Error in Commander `get_cmdr()` lookup: {er}", exc_info=True)
            raise EDSMConnectionError("Error! Unable to get commander info.")

        if len(responses) == 0:
            return None
        else:
            # Throw out data we don't need
            del responses['msgnum'], responses['msg'],\
                responses['firstDiscover'], responses['url'], responses['shipId']
            return cls(**responses, name=name)

    @classmethod
    async def location(cls, name) -> Optional[Location]:
        try:
            location = await Commander.get_cmdr(name=name)
        except EDSMConnectionError:
            raise

        if location is None:
            return None
        else:
            if location.date is None:
                time = "an unknown date and time."
            else:
                time = location.date
            return Location(system=location.system,
                            coordinates=location.coordinates,
                            time=time)


async def checkdistance(sysa: str, sysb: str):

    # Set default values
    coordsA, coordsB, is_SysA, is_SysB = 0, 0, False, False

    try:
        system1 = await GalaxySystem.get_info(name=sysa)
        system2 = await GalaxySystem.get_info(name=sysb)

        if system1 is not None:
            coordsA, is_SysA = system1.coords, True
        if system2 is not None:
            coordsB, is_SysB = system2.coords, True

    except EDSMLookupError:
        raise

    if not is_SysA:
        try:
            cmdr1 = await Commander.location(name=sysa)
            if cmdr1 is not None:
                coordsA, is_SysA = cmdr1.coordinates, True
        except EDSMLookupError:
            raise

    if not is_SysB:
        try:
            cmdr2 = await Commander.location(name=sysb)
            if cmdr2 is not None:
                coordsB, is_SysB = cmdr2.coordinates, True
        except EDSMLookupError:
            raise

    if is_SysA and is_SysB:
        distance = await calc_distance(coordsA['x'], coordsB['x'], coordsA['y'], coordsB['y'],
                                       coordsA['z'], coordsB['z'])
        distance = f'{distance:,}'
        return distance

    if not is_SysA:
        raise NoResultsEDSM(f"No system and/or commander named {sysa} was found in the EDSM database.")

    if not is_SysB:
        raise NoResultsEDSM(f"No system and/or commander named {sysb} was found in the EDSM database.")


async def checklandmarks(SysName):
    global landmarks
    # Set default values
    Coords, Is_Sys = 0, None

    try:
        system = await GalaxySystem.get_info(name=SysName)
        if system is not None:
            Coords, Is_Sys = system.coords, True
    except EDSMLookupError:
        raise

    if system is None:

        try:
            system = await Commander.location(name=SysName)
            if system is not None:
                Coords, Is_Sys = system.coordinates, True
        except EDSMLookupError:
            raise

    if system is not None:

        currclosest = None

        # Load JSON file if landmarks cache is empty, else we just get objects from the cache
        if not landmarks:
            with open('src/packages/edsm/landmarks.json') as jsonfile:
                landmarks = json.load(jsonfile)

        maxdist = config['EDSM']['Maximum landmark distance']

        for landmark in range(len(landmarks)):
            currlandmark = landmarks[landmark]['Name']
            lmx = landmarks[landmark]['Coords']['x']
            lmy = landmarks[landmark]['Coords']['y']
            lmz = landmarks[landmark]['Coords']['z']

            distancecheck = await calc_distance(Coords['x'], lmx, Coords['y'], lmy, Coords['z'], lmz)

            if float(distancecheck) < float(maxdist):
                currclosest = currlandmark
                maxdist = distancecheck

        if currclosest is not None:
            return currclosest, f'{maxdist:,}'
        else:
            raise NoResultsEDSM(f"No major landmark systems within 10,000 ly of {SysName}.")

    if not Is_Sys:
        raise NoResultsEDSM(f"No system and/or commander named {SysName} was found in the EDSM database.")


async def calc_distance(x1, x2, y1, y2, z1, z2):
    p1 = np.array([x1, y1, z1])
    p2 = np.array([x2, y2, z2])
    squared_dist = np.sum((p1 - p2) ** 2, axis=0)
    dist = np.sqrt(squared_dist)
    dist = np.around(dist, decimals=2, out=None)
    return float(dist)
