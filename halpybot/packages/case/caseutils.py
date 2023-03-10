"""
caseutils.py - Crunching the Numbers for Case Information

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
from __future__ import annotations
import re
from typing import TYPE_CHECKING
from attrs import evolve
from ..models import Case, Platform

if TYPE_CHECKING:
    from ..ircclient import HalpyBOT
    from ..announcer import AnnouncerArgs


async def create_case(args: AnnouncerArgs, codemap: Platform, client: HalpyBOT) -> int:
    """Create a Case on the board from a rescue announcement"""
    # Determine if an IRCN is needed by default

    ircn = re.search("/[^a-zA-Z0-9]/", args["CMDR"])
    if ircn:
        ircn = re.sub("/[^a-zA-Z0-9]/", "", args["CMDR"])
    # Create the base case
    newcase: Case = await client.board.add_case(
        client=args["CMDR"], platform=codemap, system=args["System"]
    )
    if ircn:
        newcase: Case = evolve(newcase, irc_nick=ircn)
    if "CanSynth" in args:
        newcase = evolve(
            newcase,
            hull_percent=int(args["Hull"]),
            canopy_broken=True,
            can_synth=args["CanSynth"],
            o2_timer=args["Oxygen"],
        )
    elif "Coords" in args:
        newcase = evolve(
            newcase,
            planet=args["Planet"],
            pcoords=args["Coords"],
            kftype=args["KFType"],
        )
    else:
        newcase = evolve(newcase, hull_percent=int(args["Hull"]))
    await client.board.mod_case(newcase.board_id, newcase)
    return newcase.board_id
