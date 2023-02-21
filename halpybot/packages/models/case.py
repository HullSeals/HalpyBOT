"""
case.py - The Case Object

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
from typing import Optional
from attrs import define, field
import pendulum


@define
class Case:
    """The Case Object - Tracking All The Things!"""

    # All Cases
    # Da Mandatories
    client_name: str
    system: str
    platform: str
    board_id: int
    creation_time: pendulum.DateTime = field(factory=lambda: pendulum.now(tz="utc"))
    updated_time: pendulum.DateTime = field(factory=lambda: pendulum.now(tz="utc"))
    active: bool = True
    # Filled As Case Continues
    dispatchers: list = field(factory=list)
    responders: list = field(factory=list)
    case_notes: list = field(factory=list)
    case_status: Optional[str] = None
    closed_to: Optional[str] = None

    # Da Optionalz
    irc_nick: Optional[str] = None

    # For Seal Cases
    hull_percent: Optional[int] = None
    canopy_broken: Optional[bool] = None

    # For Kingfisher Cases
    planet: Optional[str] = None
    pcoords: Optional[str] = None

    def board_name_ref(self):
        """Return how we are referring to the Client's name"""
        if self.irc_nick:
            return self.irc_nick
        return self.client_name


# TODOs:
# How do we define platforms, Case Status, coords, etc.?
# Can we define our lists more specifically?
