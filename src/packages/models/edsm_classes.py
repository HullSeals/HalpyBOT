"""
HalpyBOT v1.5.2

edsm_classes.py - (data)classes for the EDSM module

This module houses the API datamodel, which EXACTLY matches what EDSM
returns when queried.
It is STRONGLY recommended to not use these datatypes directly
in internal code, but to have an adapter in the middle.

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import Union, Optional
from attr import dataclass

@dataclass
class Coordinates:
    """EDSM object coordinates dictionary"""
    x: float
    y: float
    z: float

@dataclass
class SystemInfo:
    """EDSM system information dictionary"""
    allegiance: str
    government: str
    faction: str
    factionState: str
    population: int
    security: str
    economy: str


@dataclass()
class Location:
    """EDSM location object"""
    system: str
    coordinates: Coordinates
    time: Optional[str]

@dataclass
class Commander:
    # Three Keys We Care About
    msgnum: int
    system: str
    coordinates: Coordinates
    date: Optional[str]

@dataclass
class Galaxy:
    # The Keys We Care About
    name: str
    coords: Coordinates
