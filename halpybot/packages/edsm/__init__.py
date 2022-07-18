"""
__init__.py - Initilization for Elite: Dangerous Star Map API interface module

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from .edsm import (
    GalaxySystem,
    Commander,
    EDSMLookupError,
    EDSMConnectionError,
    checkdistance,
    checkdssa,
    checklandmarks,
    get_nearby_system,
    sys_cleaner,
    NoResultsEDSM,
    calc_distance,
    calc_direction,
    diversions,
    NoNearbyEDSM,
)

__all__ = [
    "GalaxySystem",
    "Commander",
    "EDSMLookupError",
    "EDSMConnectionError",
    "checklandmarks",
    "checkdssa",
    "checkdistance",
    "get_nearby_system",
    "sys_cleaner",
    "NoResultsEDSM",
    "calc_distance",
    "calc_direction",
    "diversions",
    "NoNearbyEDSM",
]
