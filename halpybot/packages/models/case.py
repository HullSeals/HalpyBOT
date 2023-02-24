"""
case.py - The Case Object

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
from typing import Optional
from enum import Enum
from attrs import define, field
from attr import dataclass
import pendulum


class Platform(Enum):
    """Storing Platform References"""

    ODYSSEY = 1
    XBOX = 2
    PLAYSTATION = 3
    LEGACY_HORIZONS = 4
    LIVE_HORIZONS = 5


class Status(Enum):
    """Saving Case Status"""

    ACTIVE = 0
    CLOSED = 1
    DELAYED = 2


@dataclass
class KFCoords:
    """KingFisher Coordinate Object"""

    x: float
    y: float


@define
class Case:
    """The Case Object - Tracking All The Things!"""

    # All Cases
    # Da Mandatories
    client_name: str
    system: str
    platform: Platform
    board_id: int
    creation_time: pendulum.DateTime = field(factory=lambda: pendulum.now(tz="utc"))
    updated_time: pendulum.DateTime = field(factory=lambda: pendulum.now(tz="utc"))
    status: Status = Status.ACTIVE
    # Filled As Case Continues
    dispatchers: list = field(factory=list)
    responders: list = field(factory=list)
    case_notes: list = field(factory=list)
    closed_to: Optional[int] = None

    # Da Optionalz
    irc_nick: Optional[str] = None

    # For Seal Cases
    hull_percent: Optional[int] = None
    canopy_broken: Optional[bool] = None

    # For Kingfisher Cases
    planet: Optional[str] = None
    pcoords: Optional[KFCoords] = None
