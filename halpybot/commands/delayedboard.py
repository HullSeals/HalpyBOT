"""
delayedboard.py - Delayed Case Board commands

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List
from loguru import logger
from ..packages.database import NoDatabaseConnection
from ..packages.delayedboard import DelayedCase
from ..packages.checks import Require, Drilled, Moderator
from ..packages.command import Commands, get_help_text
from ..packages.models import Context


@Commands.command("delaycase")
@Require.permission(Drilled)
@Require.channel()
async def cmd_create_delayed_case(ctx: Context, args: List[str]):
    """
    Create a new case on the Delayed-board

    Usage: !delaycase [case status] [notes]
    Aliases: n/a
    """
    if len(args) == 0:
        return await ctx.reply(get_help_text("delaycase"))
    # input validation
    if args[0] not in ["1", "2"]:
        return await ctx.reply("Cannot create case: no valid case mode was given.")
    if len(args[1:]) == 0:
        return await ctx.reply("Cannot create case: no notes provided by user.")

    case_status = args[0]
    message = " ".join(args[1:])

    if len(message) > 400:
        return await ctx.reply(
            "Cannot create case: maximum length for notes is 400 characters."
        )

    # Create the case
    try:
        results = await DelayedCase.open(case_status, message, ctx.sender)
    except NoDatabaseConnection:
        logger.exception("Offline Mode Set, No Database Connection")
        return await ctx.reply(
            "Cannot create case: running in OFFLINE MODE. "
            "Contact a cyberseal immediately!"
        )

    if results[3]:
        await ctx.reply(
            "WARNING: characters incompatible with the database have been removed from the notes."
        )

    if results[1] == 0:
        return await ctx.reply(
            f"Started a new Delayed Case with the ID #{results[0]} and status code {case_status}."
        )
    if results[1] == 1:
        return await ctx.reply("Cannot create case: contact a cyberseal")


@Commands.command("reopen")
@Require.permission(Moderator)
@Require.channel()
async def cmd_reopen_delayed_case(ctx: Context, args: List[str]):
    """
    Reopen a case on the Delayed-board

    Usage: !reopen [case ID] [case status]
    Aliases: n/a
    """
    if len(args) == 0:
        return await ctx.reply(get_help_text("reopen"))
    # input validation
    if len(args) < 2 or args[1] not in ["1", "2"]:
        return await ctx.reply(
            "Cannot reopen case: no valid case number/case status was provided."
        )
    if not args[0].isnumeric():
        return await ctx.reply("No valid case number was provided.")

    case_id = int(args[0])
    casestat = args[1]

    try:
        results = await DelayedCase.reopen(case_id, casestat, ctx.sender)
    except NoDatabaseConnection:
        logger.exception("Offline Mode Set, No Database Connection")
        return await ctx.reply(
            "Cannot reopen case: running in OFFLINE MODE. "
            "Contact a cyberseal immediately!"
        )

    if results[1] == 0:
        return await ctx.reply(f"Successfully reopened Delayed Case #{results[0]}.")
    logger.error("An error occured: {results}", results=str(results[2]))
    return await ctx.reply("An error occured. Contact the Cybers.")


@Commands.command("endcase", "close")
@Require.permission(Drilled)
@Require.channel()
async def cmd_close_delayed_case(ctx: Context, args: List[str]):
    """
    Close a case on the delayed board

    Usage: !endcase [case ID]
    Aliases: close
    """
    if len(args) == 0:
        return await ctx.reply(get_help_text("endcase"))
    # Input validation
    if len(args) < 1 or not args[0].isnumeric():
        return await ctx.reply("Cannot comply: no valid case number was provided.")

    case_id = int(args[0])

    try:
        results = await DelayedCase.status(
            case_id, 3, ctx.sender
        )  # set casestat to 3 to close case
    except NoDatabaseConnection:
        logger.exception("Offline Mode Set, No Database Connection")
        return await ctx.reply(
            "Cannot update case: running in OFFLINE MODE. "
            "Contact a cyberseal immediately!"
        )

    if results[1] == 0:
        return await ctx.reply(f"Case #{results[0]} closed.")
    logger.error("An error occured: {results}", results=str(results[2]))
    return await ctx.reply("An error occured. Contact the Cybers.")


@Commands.command("updatestatus")
@Require.permission(Drilled)
@Require.channel()
async def cmd_update_delayed_status(ctx: Context, args: List[str]):
    """
    Update the status of a case on the delayed board

    Usage: !updatestatus [case ID] [case status]
    Aliases: n/a
    """
    if len(args) == 0:
        return await ctx.reply(get_help_text("updatestatus"))
    # Input validation
    if len(args) < 1 or not args[0].isnumeric():
        return await ctx.reply("Cannot comply: no valid case number was provided.")

    if len(args) < 2 or args[1] not in ["1", "2"]:
        return await ctx.reply("Cannot comply: please set a valid status code")

    case_id = int(args[0])
    casestat = int(args[1])

    try:
        results = await DelayedCase.status(case_id, casestat, ctx.sender)
    except NoDatabaseConnection:
        logger.exception("Offline Mode Set, No Database Connection")
        return await ctx.reply(
            "Cannot update case: running in OFFLINE MODE. "
            "Contact a cyberseal immediately!"
        )

    if results[1] == 0:
        return await ctx.reply(f"Case #{results[0]} now has status {casestat}.")
    logger.error("An error occured: {results}", results=str(results[2]))
    return await ctx.reply("An error occured. Contact the Cybers.")


@Commands.command("updatenotes")
@Require.permission(Drilled)
@Require.channel()
async def cmd_update_delayed_notes(ctx: Context, args: List[str]):
    """
    Update the notes of a case on the delayed board

    Usage: !updatenotes [case ID] [new notes]
    Aliases n/a
    """
    if len(args) == 0:
        return await ctx.reply(get_help_text("updatenotes"))

    message = " ".join(args[1:])
    # Input validation
    if len(args) < 1 or not args[0].isnumeric():
        return await ctx.reply("Cannot comply: no valid case number was provided.")

    if len(args) < 2:
        return await ctx.reply(
            "Cannot comply: no new notes for the case were provided."
        )

    if len(message) > 400:
        return await ctx.reply(
            "Cannot update notes: maximum length for notes is 400 characters."
        )

    case_id = int(args[0])

    try:
        results = await DelayedCase.notes(case_id, message, ctx.sender)
    except NoDatabaseConnection:
        logger.exception("Offline Mode Set, No Database Connection")
        return await ctx.reply(
            "Cannot update case: running in OFFLINE MODE. "
            "Contact a cyberseal immediately!"
        )

    if results[3]:
        await ctx.reply(
            "WARNING: characters incompatible with the database have been removed from the notes."
        )

    if results[1] == 0:
        return await ctx.reply(f"Notes for case #{results[0]} have been updated.")
    logger.error("An error occured: {results}", results=str(results[2]))
    return await ctx.reply("An error occured. Contact the Cybers.")


@Commands.command("delaystatus", "checkstatus")
async def cmd_check_delayed_cases(ctx: Context, args: List[str]):
    """
    Check the Delayed Board for cases

    Usage: !delaystatus
    Aliases: checkstatus
    """

    try:
        count = await DelayedCase.check()
    except NoDatabaseConnection:
        logger.exception("Offline Mode Set, No Database Connection")
        return await ctx.reply(
            "Cannot connect to board: running in OFFLINE MODE. "
            "Contact a cyberseal immediately!"
        )

    if count == 0:
        return await ctx.reply("No Cases marked Delayed. Good Job, Seals!")
    return await ctx.reply(
        f"{count} Cases Marked as Delayed! Monitor them here: https://hullse.al/delayedCases"
    )


@Commands.command("updatecase")
@Require.permission(Drilled)
@Require.channel()
async def cmd_update_delayed_case(ctx: Context, args: List[str]):
    """
    Update details of a case on the Delayed Board

    Usage: !updatecase [case ID] (case status) (case notes)
    Aliases: n/a
    """
    if len(args) == 0:
        return await ctx.reply(get_help_text("updatecase"))
    # Input validation
    if len(args) < 1 or not args[0].isnumeric():
        return await ctx.reply("Cannot comply: no valid case number was provided.")
    if len(args) < 2:
        return await ctx.reply(
            "Cannot comply: no new case status and/or notes were provided."
        )

    # If only a new status or notes are supplied, yeet it at their own commands
    try:
        if len(args) == 2 and args[1].isnumeric():
            return await cmd_update_delayed_status(ctx, args)
        if len(args) >= 2 and not args[1].isnumeric():
            return await cmd_update_delayed_notes(ctx, args)

        # Both: call procedures back to back
        case_id = int(args[0])
        casestat = int(args[1])
        message = " ".join(args[2:])

        # One more round of input validation
        if casestat not in [1, 2]:
            return await ctx.reply("Cannot comply: please set a valid status code")

        statusout = await DelayedCase.status(case_id, casestat, ctx.sender)
        notesout = await DelayedCase.notes(case_id, message, ctx.sender)

    except NoDatabaseConnection:
        logger.exception("Offline Mode Set, No Database Connection")
        return await ctx.reply(
            "Cannot update case: running in OFFLINE MODE. "
            "Contact a cyberseal immediately!"
        )

    if notesout[3]:
        await ctx.reply(
            "WARNING: characters incompatible with the database have been removed from the notes."
        )

    if notesout[1] == 0 and statusout[1] == 0:
        return await ctx.reply(
            f"Status and notes for Case #{statusout[0]} successfully updated"
        )
    if notesout[1] != 0 or statusout[1] != 0:
        # Don't send error message twice if it's identical for status and notes
        if notesout[2] == statusout[2]:
            logger.error("An error occured: {results}", results=str(notesout[2]))
            return await ctx.reply("An error occured. Contact the Cybers.")
        logger.error(
            "An error occured: {results}, {results2}",
            results=str(notesout[2]),
            results2=str(statusout[2]),
        )
        return await ctx.reply("An error occured. Contact the Cybers.")
