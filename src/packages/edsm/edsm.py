"""
HalpyBOT v1.2.3

edsm.py - Elite: Dangerous Star Map API interface module

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from __future__ import annotations
import requests
import numpy as np
import logging
from dataclasses import dataclass
import json
from time import time
from typing import Optional, Union

from ..datamodels import SystemInfo, Coordinates, Location
from ..utils import get_time_seconds
from ..configmanager import config

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

@dataclass()
class EDSMQuery:
    object: Union[GalaxySystem, Commander, None]
    time: time()


@dataclass(frozen=True)
class GalaxySystem:
    name: str
    coords: Coordinates
    coordsLocked: bool
    information: SystemInfo

    lookupCache = {}

    @classmethod
    async def get_info(cls, name, CacheOverride: bool = False) -> Optional[GalaxySystem]:

        # Check if cached
        if name.strip().upper() in GalaxySystem.lookupCache.keys() and CacheOverride is False:
            # If less than five minutes ago return stored object
            lookuptime = GalaxySystem.lookupCache[name.strip().upper()].time
            cachetime = int(await get_time_seconds(config['EDSM']['timeCached']))
            if time() < lookuptime + cachetime:
                return GalaxySystem.lookupCache[name.strip().upper()].object

        # Else, get the system from EDSM
        try:
            response = requests.get("https://www.edsm.net/api-v1/system",
                                    params={"systemName": name,
                                            "showCoordinates": 1,
                                            "showInformation": 1})
            responses = response.json()

        except requests.exceptions.RequestException as er:
            logging.error(f"EDSM: Error in `system get_info()` lookup: {er}", exc_info=True)
            raise EDSMConnectionError("Unable to verify system, having issues connecting to the EDSM API.")

        # Return None if system doesn't exist
        if len(responses) == 0:
            sysobj = None
        else:
            sysobj = cls(**responses)

        # Store in cache and return
        GalaxySystem.lookupCache[name.strip().upper()] = EDSMQuery(sysobj, time())
        return sysobj

    @classmethod
    async def exists(cls, name, CacheOverride: bool = False) -> bool:
        try:
            obj = await cls.get_info(name, CacheOverride)
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

    lookupCache = {}

    @classmethod
    async def get_cmdr(cls, name, CacheOverride: bool = False) -> Optional[Commander]:

        # Check if cached
        if name.strip().upper() in Commander.lookupCache.keys() and CacheOverride is False:
            # If less than five minutes ago return stored object
            lookuptime = Commander.lookupCache[name.strip().upper()].time
            cachetime = int(await get_time_seconds(config['EDSM']['timeCached']))
            if time() < lookuptime + cachetime:
                return Commander.lookupCache[name.strip().upper()].object

        try:
            response = requests.get("https://www.edsm.net/api-logs-v1/get-position",
                                    params={"commanderName": name,
                                            "showCoordinates": 1})
            responses = response.json()

            # Why do we have to do this? come on, EDSM!
            if not responses['isDocked']:
                responses['station'], responses['dateDocked'] = None, None

        except (requests.exceptions.RequestException, KeyError) as er:
            logging.error(f"EDSM: Error in Commander `get_cmdr()` lookup: {er}", exc_info=True)
            raise EDSMConnectionError("Error! Unable to get commander info.")

        # Return None if cmdr doesn't exist
        if len(responses) == 0 or responses['msgnum'] == 203:
            cmdrobj = None
        else:
            # Throw out data we don't need
            del responses['msgnum'], responses['msg'], \
                responses['firstDiscover'], responses['url'], responses['shipId']
            cmdrobj = cls(**responses, name=name)

        # Store in cache and return
        Commander.lookupCache[name.strip().upper()] = EDSMQuery(cmdrobj, time())
        return cmdrobj

    @classmethod
    async def location(cls, name, CacheOverride: bool = False) -> Optional[Location]:
        try:
            location = await Commander.get_cmdr(name=name, CacheOverride=CacheOverride)
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


async def checkdistance(sysa: str, sysb: str, CacheOverride: bool = False):

    # Set default values
    coordsA, coordsB, is_SysA, is_SysB = 0, 0, False, False

    try:
        system1 = await GalaxySystem.get_info(name=sysa, CacheOverride=CacheOverride)
        system2 = await GalaxySystem.get_info(name=sysb, CacheOverride=CacheOverride)

        if system1 is not None:
            coordsA, is_SysA = system1.coords, True
        if system2 is not None:
            coordsB, is_SysB = system2.coords, True

    except EDSMLookupError:
        raise

    if not is_SysA:
        try:
            cmdr1 = await Commander.location(name=sysa, CacheOverride=CacheOverride)
            if cmdr1 is not None:
                coordsA, is_SysA = cmdr1.coordinates, True
        except EDSMLookupError:
            raise

    if not is_SysB:
        try:
            cmdr2 = await Commander.location(name=sysb, CacheOverride=CacheOverride)
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


async def checklandmarks(SysName, CacheOverride: bool = False):
    global landmarks
    # Set default values
    Coords, LMCoords, Is_Sys = 0, 0, None

    try:
        system = await GalaxySystem.get_info(name=SysName, CacheOverride=CacheOverride)
        if system is not None:
            Coords, Is_Sys = system.coords, True
    except EDSMLookupError:
        raise

    if system is None:

        try:
            system = await Commander.location(name=SysName, CacheOverride=CacheOverride)
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
            LMCoords = landmarks[landmark]['Coords']

            distancecheck = await calc_distance(Coords['x'], LMCoords['x'],
                                                Coords['y'], LMCoords['y'],
                                                Coords['z'], LMCoords['z'])
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
