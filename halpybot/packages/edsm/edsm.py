"""
HalpyBOT v1.5.2

edsm.py - Elite: Dangerous Star Map API interface module

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

Special thanks to TheUnkn0wn1 for his assistance on this module! - https://github.com/theunkn0wn1
"""

from __future__ import annotations

import typing

import aiohttp
import asyncio
import numpy as np
import logging
import math
import cattr
from pathlib import Path
from attr import dataclass
import json
from time import time
from typing import Optional, Union
from halpybot import DEFAULT_USER_AGENT
from ..models import Coordinates, Location
from ..models import edsm_classes
from ..utils import get_time_seconds
from ..configmanager import config
from ..database import Grafana

logger = logging.getLogger(__name__)
logger.addHandler(Grafana)


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
carriers = []


@dataclass()
class EDSMQuery:
    object: Union[GalaxySystem, Commander, None]
    time: time()


@dataclass
class GalaxySystem:
    """EDSM system object

    System info received from the EDSM API.

    """

    name: str
    coords: Coordinates

    _lookupCache = {}

    @classmethod
    def from_api(cls, api: edsm_classes.Galaxy) -> GalaxySystem:
        return cls(name=api.name, coords=api.coords)

    @classmethod
    async def get_info(
        cls, name, cache_override: bool = False
    ) -> Optional[GalaxySystem]:
        """Get a system object from the EDSM API.

        If the same object was requested less than
        5 minutes ago, it will be retrieved from the internal lookup cache instead. This time
        can be adjusted in config.ini

        Args:
            name (str): The system's name
            cache_override (bool): Disregard caching rules and get directly from EDSM, if true.

        Returns:
            (`GalaxySystem` or None): An EDSM system object, None if unsuccessful.

        Raises:
            EDSMConnectionError: Connection could not be established. Timeout is 10 seconds
                by default.

        """
        name = await sys_cleaner(name)
        # Check if cached
        if name in cls._lookupCache.keys() and cache_override is False:
            # If less than five minutes ago return stored object
            lookuptime = cls._lookupCache[name].time
            cachetime = int(await get_time_seconds(config["EDSM"]["timeCached"]))
            if time() < lookuptime + cachetime:
                return cls._lookupCache[name].object

        # Else, get the system from EDSM
        try:
            async with aiohttp.ClientSession(
                headers={"User-Agent": DEFAULT_USER_AGENT}
            ) as session:
                async with await session.get(
                    "https://www.edsm.net/api-v1/system",
                    params={
                        "systemName": name,
                        "showCoordinates": 1,
                        "showInformation": 1,
                    },
                    timeout=10,
                ) as response:
                    responses = await response.json()

        except aiohttp.ClientError as er:
            logger.error(
                f"EDSM: Error in `system get_info()` lookup: {er}", exc_info=True
            )
            raise EDSMConnectionError(
                "Unable to verify system, having issues connecting to the EDSM API."
            )

        # Return None if system doesn't exist
        if len(responses) == 0:
            return None
        api: edsm_classes.Galaxy = cattr.structure(responses, edsm_classes.Galaxy)

        # Store in cache and return
        sysobj = GalaxySystem.from_api(api=api)

        cls._lookupCache[name] = EDSMQuery(sysobj, time())
        return sysobj

    @classmethod
    async def exists(cls, name, cache_override: bool = False) -> bool:
        """Check if a system exists in EDSM

        This uses the same caching mechanics as get_info

        Args:
            name (str): The system's name
            cache_override (bool): Disregard caching rules and get directly from EDSM, if true.

        Returns:
            (bool): True if system exists in EDSM, else false

        Raises:
            EDSMConnectionError: Connection could not be established. Timeout is 10 seconds
                by default.

        """
        obj = await cls.get_info(name, cache_override)
        if obj is None:
            return False
        else:
            return True

    @classmethod
    async def get_nearby(cls, x, y, z):
        """Get a nearby system based on coordinates from the EDSM API.

        Args:
            x (str): The subject x coordinate
            y (str): The subject y coordinate
            z (str): The subject z coordinate

        Returns:
            (tuple): a tuple with the following values:

                - (str or None): An EDSM system object, None if unsuccessful.
                - (str or None): Dist in LY from the coords to the EDSM system object, None if unsuccessful

        Raises:
            EDSMConnectionError: Connection could not be established. Timeout is 10 seconds
                by default.

        """
        # Else, get the system from EDSM
        try:
            async with aiohttp.ClientSession(
                headers={"User-Agent": DEFAULT_USER_AGENT}
            ) as session:
                async with await session.get(
                    "https://www.edsm.net/api-v1/sphere-systems",
                    params={"x": x, "y": y, "z": z, "radius": 100, "minRadius": 1},
                    timeout=10,
                ) as response:
                    responses = await response.json()

        except aiohttp.ClientError as er:
            logger.error(
                f"EDSM: Error in `system get_info()` lookup: {er}", exc_info=True
            )
            raise EDSMConnectionError(
                "Unable to verify system, having issues connecting to the EDSM API."
            )

        # Return None if system doesn't exist
        if len(responses) == 0:
            sysname = None
            dist = None
        else:
            sysname = responses[0]["name"]
            dist = responses[0]["distance"]

        return sysname, dist


@dataclass(frozen=True)
class Commander:
    """EDSM commander object

    Commander info received from the EDSM API

    """

    # The Four Things We Care About
    msgnum: int
    name: str
    system: str
    coordinates: Coordinates
    date: Optional[str]

    _lookupCache = {}

    @classmethod
    def from_api(cls, name: str, api: edsm_classes.Commander) -> Commander:
        return cls(
            msgnum=api.msgnum,
            name=name,
            system=api.system,
            coordinates=api.coordinates,
            date=api.date,
        )

    @classmethod
    async def get_cmdr(cls, name, cache_override: bool = False) -> Optional[Commander]:
        """Get info about a CMDR from EDSM

        If the same object was requested less than
        5 minutes ago, it will be retrieved from the internal lookup cache instead. This time
        can be adjusted in config.ini

        Args:
            name (str): CMDR name
            cache_override (bool): Disregard caching rules and get directly from EDSM, if true.

        Returns:
            (`Commander` or None): Commander object if CMDR exists in EDSM, else None

        Raises:
            EDSMConnectionError: Connection could not be established. Timeout is 10 seconds
                by default.

        """

        # Check if cached
        if name.strip().upper() in cls._lookupCache.keys() and cache_override is False:
            # If less than five minutes ago return stored object
            lookuptime = cls._lookupCache[name.strip().upper()].time
            cachetime = int(await get_time_seconds(config["EDSM"]["timeCached"]))
            if time() < lookuptime + cachetime:
                return cls._lookupCache[name.strip().upper()].object

        try:
            async with aiohttp.ClientSession(
                headers={"User-Agent": DEFAULT_USER_AGENT}
            ) as session:
                async with await session.get(
                    "https://www.edsm.net/api-logs-v1/get-position",
                    params={"commanderName": name, "showCoordinates": 1},
                    timeout=10,
                ) as response:
                    responses = await response.json()

        except (aiohttp.ClientError, KeyError) as er:
            logger.error(
                f"EDSM: Error in Commander `get_cmdr()` lookup: {er}", exc_info=True
            )
            raise EDSMConnectionError("Error! Unable to get commander info.")
        # Return None if cmdr doesn't exist
        if len(responses) == 0 or responses["msgnum"] == 203:
            return None
        if responses["msgnum"] == 201:
            raise EDSMConnectionError
        api: edsm_classes.Commander = cattr.structure(responses, edsm_classes.Commander)

        if api.system is None:
            raise EDSMConnectionError("Error! CMDR Exists, but unable to get info.")

        # Store in cache and return
        cmdrobj = Commander.from_api(name=name, api=api)

        cls._lookupCache[name.strip().upper()] = EDSMQuery(cmdrobj, time())
        return cmdrobj

    @classmethod
    async def location(cls, name, cache_override: bool = False) -> Optional[Location]:
        """Get a CMDRs location

        Get a Location object for an EDSM commander.

        Args:
            name (str): CMDR name
            cache_override (bool): Disregard caching rules and get directly from EDSM, if true.

        Returns:
            (`Location` or None): CMDRs location if found, else None.

                `Location.system` is the system the cmdr is currently in.
                `Location.coordinates` can be accessed as a dict:

                {
                   "x": Union[float, int],
                   "y": Union[float, int],
                   "z": Union[float, int]
                }

        Raises:
            EDSMConnectionError: Connection could not be established. Timeout is 10 seconds
                by default.

        """
        location = await Commander.get_cmdr(name=name, cache_override=cache_override)
        if location is None:
            return None
        else:
            if location.date is None:
                location_time = "an unknown date and time."
            else:
                location_time = location.date
            return Location(
                system=location.system,
                coordinates=location.coordinates,
                time=location_time,
            )


async def checkdistance(sysa: str, sysb: str, cache_override: bool = False):
    """Check distance between two EDSM points

    Both data points must be known to EDSM.

    Args:
        sysa (str): Either a CMDR or system name
        sysb (str): Either a CMDR or system name
        cache_override (bool): Disregard caching rules and get directly from EDSM, if true.

    Returns:
        (tuple): A tuple with the following values:

            - Distance (str): formatted as xx,yyy.zz
            - Cardinal direction (str): Cardinal direction from point A to B

    Raises:
        EDSMConnectionError: Connection could not be established. Timeout is 10 seconds
                by default.
        NoResultsEDSM: No point was found for either A, B, or both.

    """

    # get both systems at the same time.
    system1, system2 = await asyncio.gather(
        GalaxySystem.get_info(name=sysa, cache_override=cache_override),
        GalaxySystem.get_info(name=sysb, cache_override=cache_override),
    )

    if system1 is None:
        # not a system, maybe a commander?
        cmdr1 = await Commander.location(name=sysa, cache_override=cache_override)
        if cmdr1 is not None:
            system_a = cmdr1.coordinates
        else:
            system_a = None
    else:
        system_a = system1.coords

    if system2 is None:
        cmdr2 = await Commander.location(name=sysb, cache_override=cache_override)
        if cmdr2 is not None:
            system_b = cmdr2.coordinates
        else:
            system_b = None
    else:
        system_b = system2.coords

    # Actually ok that we might be giving cmdr names to sys_cleaner. It won't do anything to names without - in
    if not system_a:
        raise NoResultsEDSM(
            f"No system and/or commander named '{await sys_cleaner(sysa)}' was found in the EDSM "
            f"database."
        )

    if not system_b:
        raise NoResultsEDSM(
            f"No system and/or commander named '{await sys_cleaner(sysb)}' was found in the EDSM "
            f"database."
        )

    distance = calc_distance(
        system_a.x, system_b.x, system_a.y, system_b.y, system_a.z, system_b.z
    )
    distance = f"{distance:,}"
    direction = await calc_direction(system_b.x, system_a.x, system_b.z, system_a.z)
    return distance, direction


async def checklandmarks(edsm_sys_name, cache_override: bool = False):
    """Retrieve distance between EDSM point and landmark

    The landmarks used in this function are specified in landmarks.json

    Args:
        edsm_sys_name (str): Name of the EDSM object
        cache_override (bool): Disregard caching rules and get directly from EDSM, if true.

    Returns:

        (tuple): A tuple with the following values:

            - (str): The nearest landmark within the predefined range
            - (str): Distance between point and landmark, in the format xx,yyy.zz
            - (str): The cardinal direction from the landmark to the reference system

    Raises:
        EDSMConnectionError: Connection could not be established. Timeout is 10 seconds
                by default.
        NoResultsEDSM: No point was found for `edsm_sys_name`

    """
    global landmarks  # FIXME: Similar to Carriers, fix mutable global
    # Set default values
    lm_coords = None

    coords = await get_coordinates(edsm_sys_name, cache_override)
    if coords:
        # Load JSON file if landmarks cache is empty, else we just get objects from the cache

        target = Path() / "data" / "edsm" / "landmarks.json"
        if not landmarks:
            landmarks = json.loads(target.read_text())
            landmarks = cattr.structure(landmarks, typing.List[GalaxySystem])

        maxdist = config["EDSM"]["Maximum landmark distance"]
        distances = {
            calc_distance(
                coords.x,
                item.coords.x,
                coords.y,
                item.coords.y,
                coords.z,
                item.coords.z,
            ): item
            for item in landmarks
        }
        minimum_key = min(distances)
        minimum = distances[minimum_key]

        if minimum_key < float(maxdist):
            direction = await calc_direction(
                coords.x, minimum.coords.x, coords.z, minimum.coords.z
            )
            return minimum.name, f"{minimum_key:,}", direction
        else:
            raise NoResultsEDSM(
                f"No major landmark systems within 10,000 ly of {await sys_cleaner(edsm_sys_name)}."
            )

    if not coords:
        raise NoResultsEDSM(
            f"No system and/or commander named {await sys_cleaner(edsm_sys_name)} was found in the EDSM"
            f" database."
        )


async def checkdssa(edsm_sys_name, cache_override: bool = False):
    """Check distance to nearest DSSA carrier

    Last updated 2021-03-22 w/ 93 Carrier

    Args:
        edsm_sys_name (str): System name
        cache_override (bool): Disregard caching rules and get directly from EDSM, if true.

    Returns:
        (str): Distance between point and DSSA carrier, in the format xx,yyy.zz

    Raises:
        EDSMConnectionError: Connection could not be established. Timeout is 10 seconds
                by default.
        NoResultsEDSM: No point was found for `edsm_sys_name`.


    """
    global carriers  # FIXME: REMOVE MUTABLE GLOBAL (BAD BAD BAD)
    # Set default values
    lm_coords, maxdist = None, None

    coords = await get_coordinates(edsm_sys_name, cache_override)

    if coords:

        # Load JSON file if dssa cache is empty, else we just get objects from the cache
        target = Path() / "data" / "edsm" / "dssa.json"
        if not carriers:
            carriers = json.loads(target.read_text())
            carriers = cattr.structure(carriers, typing.List[GalaxySystem])

        distances = {
            calc_distance(
                coords.x,
                item.coords.x,
                coords.y,
                item.coords.y,
                coords.z,
                item.coords.z,
            ): item
            for item in carriers
        }

        minimum_key = min(distances)
        minimum = distances[minimum_key]

        direction = await calc_direction(
            coords.x, minimum.coords.x, coords.z, minimum.coords.z
        )
        return minimum.name, f"{minimum_key:,}", direction

    if not coords:
        raise NoResultsEDSM(
            f"No system and/or commander named {await sys_cleaner(edsm_sys_name)} was found in the EDSM"
            f" database."
        )


def calc_distance(x1, x2, y1, y2, z1, z2):
    """Calculate distance XYZ -> XYZ

    Only call this method directly when the coordinates of both points are known. If
    only the point names are known, use `edsm/checkdistance` instead.

    Args:
        x1 (int or float): X-coordinate of point A
        x2 (int or float): X-coordinate of point B
        y1 (int or float): Y-coordinate of point A
        y2 (int or float): Y-coordinate of point B
        z1 (int or float): Z-coordinate of point A
        z2 (int or float): Z-coordinate of point B

    Returns:
        (float): Distance between two points

    """
    p1 = np.array([x1, y1, z1])
    p2 = np.array([x2, y2, z2])
    squared_dist = np.sum((p1 - p2) ** 2, axis=0)
    dist = np.sqrt(squared_dist)
    dist = np.around(dist, decimals=2)
    return float(dist)


async def calc_direction(x1, x2, y1, y2):
    """Calculate direction

    Uses some Fancy Math™ to determine the approximate
    cardinal direction in 2D space between two points.

    Args:
        x1 (int or float): X-coordinate of point A
        x2 (int or float): X-coordinate of point B
        y1 (int or float): Y-coordinate of point A
        y2 (int or float): Y-coordinate of point B

    Returns:
        (str): Cardinal direction from A to B, one of the following values:

            * North
            * NE
            * East
            * SE
            * South
            * SW
            * West
            * NW

    """
    # Treat the coordinates like a right triangle - this is Trig that I swore off of after high school.
    xdeterminer = x2 - x1
    ydeterminer = y2 - y1
    degrees_temp = math.atan2(xdeterminer, ydeterminer) / math.pi * 180
    # All Coordinates must be Positive.
    if degrees_temp < 0:
        degrees_final = 360 + degrees_temp
    else:
        degrees_final = degrees_temp
    # Round to the nearest degree, treat Directions as an array and compass_lookup as the array item number.
    directions = ["North", "NE", "East", "SE", "South", "SW", "West", "NW", "North"]
    compass_lookup = round(degrees_final / 45)
    result = f"{directions[compass_lookup]}"
    return result


async def get_coordinates(edsm_sys_name: str, cache_override: bool = False):
    coords = None
    sys = await GalaxySystem.get_info(name=edsm_sys_name, cache_override=cache_override)
    if sys:
        coords = sys.coords
    if not sys:
        cmdr = await Commander.location(
            name=edsm_sys_name, cache_override=cache_override
        )
        if cmdr:
            coords = cmdr.coordinates
    return coords


async def get_nearby_system(sys_name: str, cache_override: bool = False):
    name_to_check = await sys_cleaner(sys_name)
    for _ in range(5):
        try:
            async with aiohttp.ClientSession(
                headers={"User-Agent": DEFAULT_USER_AGENT}
            ) as session:
                async with await session.get(
                    "https://www.edsm.net/api-v1/systems",
                    params={"systemName": name_to_check},
                    timeout=10,
                ) as response:
                    responces = await response.json()
            if responces:
                sys = responces[0]["name"]
                return True, sys

            # Cheeky bottom test to not include spaces in the repeat queries and not include it in the 5 request cap
            while True:
                name_to_check = name_to_check[:-1]
                if name_to_check[-1] != " ":
                    break
        except aiohttp.ClientError as er:
            logger.error(
                f"EDSM: Error in `get_nearby_system()` lookup: {er}", exc_info=True
            )
    return False, None


async def sys_cleaner(sys_name: str):
    orig_sys = sys_name
    sys_name = " ".join(sys_name.split())
    sys_name = sys_name.upper()

    try:
        if "-" in sys_name:
            sys_name_list = sys_name.split()
            sys_name = ""
            for index, block in enumerate(sys_name_list):
                sys_name += block + " "
                if "-" in block:
                    sys_name += sys_name_list[index + 1]
                    break

            swaps = {"0": "O", "1": "I", "5": "S", "8": "B"}
            unswaps = {value: key for key, value in swaps.items()}
            sys_name_parts = sys_name.split()

            # Final part is either LN or LN-N, so [1:] is N or N-N
            letter = sys_name_parts[-1][0]
            tmp = swaps[letter] if letter in swaps else letter
            for char in sys_name_parts[-1][1:]:
                if char in unswaps:
                    tmp += unswaps[char]
                else:
                    tmp += char
            sys_name_parts[-1] = tmp

            # This part it LL-L
            tmp = ""
            for char in sys_name_parts[-2]:
                if char in swaps:
                    tmp += swaps[char]
                else:
                    tmp += char
            sys_name_parts[-2] = tmp

            sys_name = " ".join(sys_name_parts)
    except IndexError:
        logger.info(
            f"System cleaner thought {sys_name} was proc-gen and could not correct formatting"
        )
        return sys_name.strip()

    logger.debug(f"System cleaner produced {sys_name} from {orig_sys}")
    return sys_name.strip()
