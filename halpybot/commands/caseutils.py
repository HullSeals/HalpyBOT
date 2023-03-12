"""
caseutils.py - Commands involving the management of Seal cases

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
from typing import List, Union
from pendulum import now
from halpybot import config
from ..packages.command import Commands, get_help_text
from ..packages.edsm import sys_cleaner
from ..packages.models import Context, User, NoUserFound, Case, Status
from ..packages.checks import Require, Drilled


async def get_case(ctx: Context, case_arg: str) -> Case:
    """Fetch a case from the Board"""
    try:
        caseref: Union[str, int] = int(case_arg)
    except ValueError:
        caseref = case_arg
    return ctx.bot.board.return_rescue(caseref)


@Commands.command("go")
async def cmd_go(ctx: Context, args: List[str]):
    """
    Check if an assigned Seal is trained and Identified before sending.

    Usage: !go [seals]
    Aliases: n/a
    """
    # If no args presented, skip the user check. This will be removed in later versions, args will be required.
    if args:
        # Clean out the list, only pass "full" args.
        args = [x.strip(" ") for x in args]
        args = [ele for ele in args if ele.strip()]
        # Loop through the list, checking each to see if they are actually a user.
        for seal in args:
            user_level = 1
            # AttributeError is thrown if a user does not exist. Accept and move on.
            try:
                whois = await User.get_info(ctx.bot, str(seal))
                vhost = User.process_vhost(whois.hostname)
            except (AttributeError, NoUserFound):
                vhost = "notUser"
            # There is no hard set "not a seal" vhost level.
            if vhost is None:
                user_level = 0
            if user_level == 0:
                await ctx.reply(
                    f"{ctx.sender}: {str(seal)} is not identified as a trained seal. Have them check their "
                    f"IRC setup?"
                )

    return await ctx.reply(
        await ctx.bot.facts.fact_formatted(fact=("go", "en"), arguments=args)
    )


@Commands.command("listboard")
@Require.permission(Drilled)
async def cmd_listboard(ctx: Context, args: List[str]):
    """
    Send a user the key details of every case on the board in DMs

    Usage: !listboard
    Aliases: n/a
    """
    caseboard = ctx.bot.board.by_id
    if not caseboard:
        return await ctx.redirect("The case board is empty!")
    message = "Here's the current case board:\n"
    for case in caseboard.values():
        hskf = "Seal" if case.hull_percent else "Fisher" if case.planet else "Unknown"
        long_ago = now(tz="utc").diff(case.updated_time).in_words()
        plt = case.platform.name.replace("_", " ")
        message += (
            f"Case {case.board_id}: Client: {case.client_name}, Platform: {plt}, "
            f"Type: {hskf}, Status: {case.status.name}, Updated: {long_ago} ago.\n"
        )
    return await ctx.redirect(f"{message}{len(caseboard)} Cases on the Board.")


@Commands.command("listcase")
@Require.permission(Drilled)
async def cmd_listcase(ctx: Context, args: List[str]):
    """
    Send a user the key details of a case on the board in DMs

    Usage: !listcase [board ID]
    Aliases: n/a
    """
    if not args:
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, "listcase"))
    try:
        case: Case = await get_case(ctx, args[0])
    except KeyError:
        return await ctx.redirect(f"No case found for {args[0]!r}.")
    return await ctx.redirect(f"{case}")


@Commands.command("rename")
@Require.permission(Drilled)
@Require.channel()
async def cmd_renamecase(ctx: Context, args: List[str]):
    """
    Rename the user of an active case

    Usage: !rename [board ID] [new name]
    Aliases: n/a
    """
    if len(args) < 2:
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, "rename"))
    try:
        case: Case = await get_case(ctx, args[0])
    except KeyError:
        return await ctx.reply(f"No case found for {args[0]!r}.")
    try:
        await ctx.bot.board.rename_case(args[1], case, ctx.sender)
    except (AssertionError, ValueError) as err:
        return await ctx.reply(str(err))
    for channel in config.channels.rescue_channels:
        await ctx.bot.message(
            channel,
            f"Client for case {case.board_id} set to {args[1]!r} from {case.client_name!r}",
        )


@Commands.command("ircn")
@Require.permission(Drilled)
@Require.channel()
async def cmd_ircn(ctx: Context, args: List[str]):
    """
    Rename the user of an active case

    Usage: !ircn [board ID] [valid IRC user]
    Aliases: n/a
    """
    if not args:
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, "ircn"))
    try:
        await User.get_info(ctx.bot, args[1])
    except (AttributeError, NoUserFound):
        return await ctx.reply("That's not an IRC user!")
    try:
        case: Case = await get_case(ctx, args[0])
    except KeyError:
        return await ctx.reply(f"No case found for {args[0]!r}.")
    new_details = {"irc_nick": args[1]}
    action = "IRC Name"
    try:
        await ctx.bot.board.mod_case(case.board_id, action, ctx.sender, **new_details)
    except ValueError as val_err:
        return await ctx.reply(str(val_err))
    for channel in config.channels.rescue_channels:
        await ctx.bot.message(
            channel,
            f"IRC Name for case {case.board_id} set to {args[1]!r} from {case.irc_nick!r}.",
        )


@Commands.command("system")
@Require.permission(Drilled)
@Require.channel()
async def cmd_system(ctx: Context, args: List[str]):
    """
    Change the system of an active case

    Usage: !rename [board ID] [new system]
    Aliases: n/a
    TODO: Can we call Landmark from here?
    """
    if len(args) < 2:
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, "system"))
    try:
        case: Case = await get_case(ctx, args[0])
    except KeyError:
        return await ctx.reply(f"No case found for {args[0]!r}.")
    newsys: str = " ".join(args[1:])
    newsys = await sys_cleaner(newsys)
    new_details = {"system": newsys}
    action = "Client System"
    try:
        await ctx.bot.board.mod_case(case.board_id, action, ctx.sender, **new_details)
    except ValueError as val_err:
        return await ctx.reply(str(val_err))
    for channel in config.channels.rescue_channels:
        await ctx.bot.message(
            channel,
            f"System for case {case.board_id} set to {newsys!r} from {case.system!r}",
        )


@Commands.command("status")
@Require.permission(Drilled)
@Require.channel()
async def cmd_status(ctx: Context, args: List[str]):
    """
    Change the activity status of a case

    Usage: !status [board ID] [new status]
    Aliases: n/a
    """
    if len(args) < 2:
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, "active"))
    try:
        case: Case = await get_case(ctx, args[0])
    except KeyError:
        return await ctx.reply(f"No case found for {args[0]!r}.")
    try:
        status = Status[args[1].upper()]
        if status == Status.CLOSED:
            raise KeyError  # Mock a KeyError. This command can't close a case.
    except KeyError:
        return await ctx.reply("Invalid case status provided.")
    new_details = {"status": status}
    action = "Case Status"
    try:
        await ctx.bot.board.mod_case(case.board_id, action, ctx.sender, **new_details)
    except ValueError:
        return await ctx.reply(f"{action} is already set to {status.name}.")
    for channel in config.channels.rescue_channels:
        await ctx.bot.message(
            channel,
            f"Status for case {case.board_id} set to {status.name!r} from {case.status.name!r}",
        )
