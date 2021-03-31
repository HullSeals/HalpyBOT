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
