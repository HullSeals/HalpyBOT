"""
edsm_classes.py - (data)classes for the EDSM module

This module houses the API datamodel, which EXACTLY matches what EDSM
returns when queried.
It is STRONGLY recommended to not use these datatypes directly
in internal code, but to have an adapter in the middle.

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import Optional
from attrs import define


@define(frozen=True)
class Coordinates:
    """EDSM object coordinates dictionary"""

    x: float
    y: float
    z: float


@define(frozen=True)
class SystemInfo:
    """EDSM system information dictionary"""

    allegiance: str
    government: str
    faction: str
    factionState: str
    population: int
    security: str
    economy: str


@define(frozen=True)
class Location:
    """EDSM location object"""

    system: str
    coordinates: Coordinates
    time: Optional[str]


@define(frozen=True)
class Commander:
    """The Commander keys we care about"""

    msgnum: int
    system: str
    coordinates: Coordinates
    date: Optional[str]


@define(frozen=True)
class Galaxy:
    """Galaxy Keys we care about"""

    name: str
    coords: Coordinates


@define()
class Point:
    """An EDSM Valid System and a Cleaner Name"""

    name: str
    pretty: Optional[str] = None


@define()
class Points:
    """A pair of valid EDSM Points"""

    point_a: Point
    point_b: Point
    jump_range: Optional[float] = None
