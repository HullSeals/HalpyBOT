"""
caseutils.py - Crunching the Numbers for Case Information

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
from __future__ import annotations
import re
from typing import TYPE_CHECKING, Union, Optional
from ..models import Case, Platform, CaseType, Context
from ... import config

if TYPE_CHECKING:
    from ..ircclient import HalpyBOT
    from ..announcer import AnnouncerArgs


async def create_case(args: AnnouncerArgs, codemap: Platform, client: HalpyBOT) -> int:
    """Create a Case on the board from a rescue announcement"""
    # Determine Type of Case
    if "CanSynth" in args:  # CB
        case_type = CaseType.BLACK
    elif "Coords" in args:  # KF
        case_type = CaseType.FISH
    else:
        case_type = CaseType.SEAL

    # Create the base case
    newcase: Case = await client.board.add_case(
        client=args["CMDR"],
        platform=codemap,
        system=args["System"],
        case_type=case_type,
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
    if case_type == CaseType.BLACK:  # CB
        evolve_args.update(
            {
                "case_type": case_type,
                "canopy_broken": True,
                "can_synth": args["CanSynth"],
                "o2_timer": args["Oxygen"],
                "hull_percent": int(args["Hull"]),
            }
        )
    if case_type == CaseType.FISH:  # kf
        evolve_args.update(
            {
                "case_type": case_type,
                "planet": args["Planet"],
                "pcoords": args["Coords"],
                "kftype": args["KFType"],
            }
        )
    else:  # Must be standard Seal
        evolve_args.update(
            {
                "case_type": case_type,
                "hull_percent": int(args["Hull"]),
            }
        )
    # Call the wrapped evolve function with **kwargs
    await client.board.mod_case(newcase.board_id, **evolve_args)
    return newcase.board_id


async def get_case(ctx: Context, case_arg: str) -> Case:
    """Fetch a case from the Board"""
    try:
        caseref: Union[str, int] = int(case_arg)
    except ValueError:
        caseref = case_arg
    return ctx.bot.board.return_rescue(caseref)


async def update_single_elem_case_prep(
    ctx: Context, case: Case, action: str, new_details, enum: bool = False
) -> Optional[str]:
    """
    Send the updated case details to the board, and handle errors
    NOTE: Can only handle a single updated value at a time.
    """
    # Get the to-be-updated element
    first_updated = next(iter((new_details.items())))
    new_key = first_updated[0]
    new_item = first_updated[1]
    try:
        await ctx.bot.board.mod_case(case.board_id, action, ctx.sender, **new_details)
    except ValueError:
        return f"{action} is already set to {new_item.name if enum else new_item}."
    for channel in config.channels.rescue_channels:
        await ctx.bot.message(
            channel,
            f"{action} for case {case.board_id} set to {new_item.name if enum else new_item!r} "
            f"from {getattr(case, new_key).name if enum else getattr(case, new_key)!r}",
        )
