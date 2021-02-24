"""
HalpyBOT v1.1

delayed.py - Delayed Case Board commands

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List
from ..database.delayedboard import create_delayed_case, reopen_delayed_case, update_delayed_status
from ..util.checks import require_channel, require_permission, DeniedMessage

@require_permission(req_level="DRILLED", message=DeniedMessage.GENERIC)
@require_channel()
async def cmd_createDelayedCase(ctx, args: List[str]):
    """
    Create a new case on the Delayed-board

    Usage: !delaycase [case status] [notes]
    Aliases: n/a
    """
    # input validation
    if len(args) == 0 or args[0] not in '12':
        return await ctx.reply("Cannot create case: no valid case mode was given.")
    if len(args[1:]) == 0:
        return await ctx.reply("Cannot create case: no notes provided by user.")

    case_status = args[0]
    message = ' '.join(args[1:])

    if len(message) > 400:
        return await ctx.reply("Cannot create case: maximum length for notes is 400 characters.")

    # Create the case
    results = await create_delayed_case(case_status, message, ctx.sender)

    if results[1] == 0:
        return await ctx.reply(f"Started a new Delayed Case with the ID #{results[0]} and status code {case_status}.")
    elif results[1] == 1:
        return await ctx.reply("Cannot create case: contact a cyberseal")


@require_permission(req_level="MODERATOR", message=DeniedMessage.MODERATOR)
@require_channel()
async def cmd_ReopenDelayedCase(ctx, args: List[str]):
    """
    Reopen a case on the Delayed-board

    Usage: !updatecase [case ID] (case status) (case notes)
    Aliases: n/a
    """
    # input validation
    if len(args) < 2 or args[1] not in '12':
        return await ctx.reply("Cannot reopen case: no valid case number/case status was provided.")
    elif not args[0].isnumeric():
        return await ctx.reply("No valid case number was provided.")

    cID = int(args[0])
    casestat = args[1]
    results = await reopen_delayed_case(cID, casestat, ctx.sender)

    if results[1] == 0:
        return await ctx.reply(f"Successfully reopened Delayed Case #{results[0]}.")
    else:
        return await ctx.reply(str(results[2]))


@require_permission(req_level="DRILLED", message=DeniedMessage.GENERIC)
@require_channel()
async def cmd_closeDelayedCase(ctx, args: List[str]):
    """
    Close a case on the delayed board

    Usage: !endcase [case ID]
    Aliases: close
    """
    # Input validation
    if len(args) < 1 or not args[0].isnumeric():
        return await ctx.reply("Cannot comply: no valid case number was provided.")

    cID = int(args[0])
    results = await update_delayed_status(cID, 3, ctx.sender)  # set casestat to 3 to close case

    if results[1] == 0:
        return await ctx.reply(f"Case #{results[0]} closed.")
    else:
        return await ctx.reply(str(results[2]))