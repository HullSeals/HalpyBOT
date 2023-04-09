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
    checkdistance,
    checkdssa,
    checklandmarks,
    get_nearby_system,
    calc_distance,
    calc_direction,
    diversions,
)

__all__ = [
    "GalaxySystem",
    "Commander",
    "checklandmarks",
    "checkdssa",
    "checkdistance",
    "get_nearby_system",
    "calc_distance",
    "calc_direction",
    "diversions",
]
