from typing import *
from dataclasses import dataclass

class Coordinates(TypedDict):
    x: Union[float, int]
    y: Union[float, int]
    z: Union[float, int]

class SystemInfo(TypedDict):
    allegiance: str
    government: str
    faction: str
    factionState: str
    population: int
    security: str
    economy: str

@dataclass()
class Location:
    system: str
    coordinates: Coordinates
    time: Optional[str]
