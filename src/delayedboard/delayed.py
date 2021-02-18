"""
HalpyBOT v1.1

database.py - Main database interaction module

Copyright (c) 2021 The Hull Seals,
All rights reserved

Licensed under the GNU General Public License
See license.md
"""

from typing import List
from ..database.database import create_delayed_case
from ..util.checks import require_channel, require_permission, DeniedMessage

@require_permission(req_level="DRILLED", message=DeniedMessage.GENERIC)
@require_channel()
async def createDelayedCase(ctx, args: List[str]):
    """
    Create a new case on the Delayed-board

    Usage: !ufi
    Aliases: n/a
    """
    # Sanity check
    if len(args) == 0 or args[0] not in '12':
        return await ctx.reply("Cannot create case: no valid case mode was given.")
    if len(args[1:]) == 0:
        return await ctx.reply("Cannot create case: no notes provided by user.")
    case_status = args[0]
    message = ' '.join(args[1:])

    # Create the case
    results = await create_delayed_case(ctx, case_status, message)

    if results[1] == 0:
        return await ctx.reply(f"Started a new Delayed Case with the ID #{results[0]} and status code {case_status}.")
    elif results[1] == 1:
        return await ctx.reply("Cannot create case: contact a cyberseal")
