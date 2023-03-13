"""
caseutils.py - Commands involving the management of Seal cases

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
from typing import List
from pendulum import now
from halpybot import config
from ..packages.command import Commands, get_help_text
from ..packages.edsm import sys_cleaner
from ..packages.models import Context, User, NoUserFound, Case, Status, CaseType
from ..packages.checks import Require, Drilled
from ..packages.case import get_case, update_single_elem_case_prep


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
    if len(args) < 2:
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
    update = await update_single_elem_case_prep(ctx, case, action, new_details)
    if update:
        return await ctx.reply(update)


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
    update = await update_single_elem_case_prep(ctx, case, action, new_details)
    if update:
        return await ctx.reply(update)


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
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, "status"))
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
    update = await update_single_elem_case_prep(
        ctx, case, action, new_details, enum=True
    )
    if update:
        return await ctx.reply(update)


@Commands.command("hull")
@Require.permission(Drilled)
@Require.channel()
async def cmd_hull(ctx: Context, args: List[str]):
    """
    Change the starting hull percentage of a case

    Usage: !hull [board ID] [new hull %]
    Aliases: n/a
    """
    if len(args) < 2:
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, "hull"))
    try:
        case: Case = await get_case(ctx, args[0])
    except KeyError:
        return await ctx.reply(f"No case found for {args[0]!r}.")
    try:
        percent = int(args[1])
        if not 0 <= percent <= 100:
            raise ValueError  # Mock a Value Error for invalid Hull Percentage
    except ValueError:
        return await ctx.reply(f"{args[1]!r} isn't a valid hull percentage")
    new_details = {"hull_percent": percent}
    action = "Hull Percentage"
    update = await update_single_elem_case_prep(ctx, case, action, new_details)
    if update:
        return await ctx.reply(update)


@Commands.command("changetype")
@Require.permission(Drilled)
@Require.channel()
async def cmd_changetype(ctx: Context, args: List[str]):
    """
    Change the case type between Seal, KF, Black, or Blue.

    Usage: !hull [board ID] [new type]
    Aliases: n/a

    SEAL = 1
    BLACK = 2
    BLUE = 3
    FISH = 4
    """
    if len(args) < 2:
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, "changetype"))
    try:
        case: Case = await get_case(ctx, args[0])
    except KeyError:
        return await ctx.reply(f"No case found for {args[0]!r}.")
    potential_type = args[1].casefold()
    if potential_type == "seal":
        new_type = CaseType.SEAL
    elif potential_type in ("kf", "fisher", "fish", "kingfish", "kingfisher"):
        new_type = CaseType.FISH
    elif potential_type == "blue":
        new_type = CaseType.BLUE
    elif potential_type in ("black", "cb"):
        new_type = CaseType.BLACK
    else:
        return await ctx.reply("Invalid New Case Type Given.")
    new_details = {"case_type": new_type}
    action = "Case Type"
    update = await update_single_elem_case_prep(
        ctx, case, action, new_details, enum=True
    )
    if update:
        return await ctx.reply(update)
