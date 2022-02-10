"""
HalpyBOT v1.5

edsm_classes.py - (data)classes for the EDSM module

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import TypedDict, Union, Optional
from dataclasses import dataclass


class Coordinates(TypedDict):
    """EDSM object coordinates dictionary"""
    x: Union[float, int]
    y: Union[float, int]
    z: Union[float, int]


class SystemInfo(TypedDict):
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
