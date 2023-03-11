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
from ..models import Case, Platform

if TYPE_CHECKING:
    from ..ircclient import HalpyBOT
    from ..announcer import AnnouncerArgs


async def create_case(args: AnnouncerArgs, codemap: Platform, client: HalpyBOT) -> int:
    """Create a Case on the board from a rescue announcement"""
    # Create the base case
    newcase: Case = await client.board.add_case(
        client=args["CMDR"], platform=codemap, system=args["System"]
    )
    evolve_args = {
        "irc_nick": newcase.client_name,
    }
    # Determine if a different IRCN is needed by default
    ircn = re.search(r"[^a-zA-Z0-9]", newcase.client_name)
    if ircn:
        ircn = re.sub(r"[^a-zA-Z0-9]", "", newcase.client_name)
        # If IRCN needed
        evolve_args.update(
            {
                "irc_nick": ircn,
            }
        )
    if evolve_args["irc_nick"][0].isdigit():
        ircn = evolve_args["irc_nick"]
        ircn = f"CMDR_{ircn}"
        evolve_args.update(
            {
                "irc_nick": ircn,
            }
        )

    # What type of case are we dealing with?
    if "CanSynth" in args:  # CB
        evolve_args.update(
            {
                "canopy_broken": True,
                "can_synth": args["CanSynth"],
                "o2_timer": args["Oxygen"],
                "hull_percent": int(args["Hull"]),
            }
        )
    elif "Coords" in args:  # KF
        evolve_args.update(
            {
                "planet": args["Planet"],
                "pcoords": args["Coords"],
                "kftype": args["KFType"],
            }
        )
    else:  # Must be standard Seal
        evolve_args.update(
            {
                "hull_percent": int(args["Hull"]),
            }
        )
    # Call the wrapped evolve function with **kwargs
    await client.board.mod_case(newcase.board_id, **evolve_args)
    return newcase.board_id
