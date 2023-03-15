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
from ..packages.models import (
    Context,
    User,
    NoUserFound,
    Case,
    Status,
    CaseType,
    Platform,
)
from ..packages.checks import Require, Drilled
from ..packages.case import get_case, update_single_elem_case_prep


# FACT WRAPPERS
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


# BOARD AND CASE LISTING
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


# CASE MANAGEMENT
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
    update = await update_single_elem_case_prep(
        ctx=ctx, case=case, action="IRC Name", new_key="irc_nick", new_item=args[1]
    )
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
    update = await update_single_elem_case_prep(
        ctx=ctx, case=case, action="Client System", new_key="system", new_item=newsys
    )
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
    update = await update_single_elem_case_prep(
        ctx=ctx,
        case=case,
        action="Case Status",
        new_key="status",
        new_item=status,
        enum=True,
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
    if case.case_type not in (CaseType.BLACK, CaseType.BLUE, CaseType.SEAL):
        return await ctx.reply("Hull can't be changed for non-Seal case")
    try:
        percent = int(args[1])
        if not 0 <= percent <= 100:
            raise ValueError  # Mock a Value Error for invalid Hull Percentage
    except ValueError:
        return await ctx.reply(f"{args[1]!r} isn't a valid hull percentage")
    update = await update_single_elem_case_prep(
        ctx=ctx,
        case=case,
        action="Hull Percentage",
        new_key="hull_percent",
        new_item=percent,
    )
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
    update = await update_single_elem_case_prep(
        ctx=ctx,
        case=case,
        action="Case Type",
        new_key="case_type",
        new_item=new_type,
        enum=True,
    )
    if update:
        return await ctx.reply(update)


@Commands.command("platform")
@Require.permission(Drilled)
@Require.channel()
async def cmd_platform(ctx: Context, args: List[str]):
    """
    Change the platform a case is on.

    Usage: !platform [board ID] [new type]
    Aliases: n/a

    ODYSSEY = 1
    XBOX = 2
    PLAYSTATION = 3
    LEGACY_HORIZONS = 4
    LIVE_HORIZONS = 5
    UNKNOWN = 6
    """
    if len(args) < 2:
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, "platform"))
    try:
        case: Case = await get_case(ctx, args[0])
    except KeyError:
        return await ctx.reply(f"No case found for {args[0]!r}.")
    potential_plt = args[1].casefold()
    if potential_plt in ("odyssey", "ody", "pc", "pc-o"):
        new_plt = Platform.ODYSSEY
    elif potential_plt in ("xbx", "xb", "xbox"):
        new_plt = Platform.XBOX
    elif potential_plt in ("ps4", "ps", "playstation"):
        new_plt = Platform.PLAYSTATION
    elif potential_plt in ("live", "horizons-live"):
        new_plt = Platform.LIVE_HORIZONS
    elif potential_plt in ("legacy", "legacy-horizons"):
        new_plt = Platform.LEGACY_HORIZONS
    else:
        return await ctx.reply("Invalid New Case Type Given.")
    update = await update_single_elem_case_prep(
        ctx=ctx,
        case=case,
        action="Case Platform",
        new_key="platform",
        new_item=new_plt,
        enum=True,
    )
    if update:
        return await ctx.reply(update)


# NOTES MANAGEMENT
@Commands.command("notes", "updatenotes", "addnote")
@Require.permission(Drilled)
@Require.channel()
async def cmd_notes(ctx: Context, args: List[str]):
    """
    Append a new entry to the Notes

    Usage: !notes [board ID] [new note line]
    Aliases: updatenotes, addnote
    """
    if len(args) < 2:
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, "notes"))
    try:
        case: Case = await get_case(ctx, args[0])
    except KeyError:
        return await ctx.reply(f"No case found for {args[0]!r}.")
    new_notes = f"{' '.join(args[1:])} - {ctx.sender} ({now(tz='UTC')})"
    notes: List[str] = case.case_notes
    notes.append(new_notes)
    await ctx.bot.board.mod_case_notes(case_id=case.board_id, new_notes=notes)
    return await ctx.reply(f"Notes for case {case.board_id} updated.")


@Commands.command("listnotes")
@Require.permission(Drilled)
async def cmd_listnotes(ctx: Context, args: List[str]):
    """
    List out just the case notes to DMs

    Usage: !listnotes [board ID]
    Aliases: n/a
    """
    if not args:
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, "notes"))
    try:
        case: Case = await get_case(ctx, args[0])
    except KeyError:
        return await ctx.reply(f"No case found for {args[0]!r}.")
    if not case.case_notes:
        return await ctx.reply(f"No Notes Found for case {case.board_id}")
    notes: str = ""
    for line_num, note in enumerate(case.case_notes, start=1):
        notes += f"{line_num}: {note}\n"
    return await ctx.redirect(notes)


@Commands.command("delnote")
@Require.permission(Drilled)
@Require.channel()
async def cmd_delnote(ctx: Context, args: List[str]):
    """
    Delete a line of the notes for a given case

    Usage: !delnote [board ID] [note index]
    TODO: Can we get an "Are you sure?" check here?
    """
    if len(args) < 2:
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, "delnote"))
    try:
        case: Case = await get_case(ctx, args[0])
    except KeyError:
        return await ctx.reply(f"No case found for {args[0]!r}.")
    if not case.case_notes:
        return await ctx.reply(f"No Notes Found for case {case.board_id}")
    try:
        del_index = int(args[1])
        del_index -= 1  # Human Indexes Start at 1. Translate it to proper array.
    except ValueError:
        return await ctx.reply("Invalid Note Index provided!")
    notes: List[str] = case.case_notes
    del notes[del_index]
    await ctx.bot.board.mod_case_notes(case_id=case.board_id, new_notes=notes)
    return await ctx.reply(f"Notes for case {case.board_id} updated.")


@Commands.command("editnote")
@Require.permission(Drilled)
@Require.channel()
async def cmd_editnote(ctx: Context, args: List[str]):
    """
    Alter a line of the notes for a given case

    Usage: !editnote [board ID] [note index] [new note content]
    TODO: Can we get an "Are you sure?" check here?
    """
    if len(args) < 3:
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, "editnote"))
    try:
        case: Case = await get_case(ctx, args[0])
    except KeyError:
        return await ctx.reply(f"No case found for {args[0]!r}.")
    if not case.case_notes:
        return await ctx.reply(f"No Notes Found for case {case.board_id}")
    try:
        note_index = int(args[1])
        note_index -= 1  # Human Indexes Start at 1. Translate it to proper array.
    except ValueError:
        return await ctx.reply("Invalid Note Index provided!")
    notes: List[str] = case.case_notes
    notes[note_index] = f"{' '.join(args[2:])} - {ctx.sender} ({now(tz='UTC')})"
    await ctx.bot.board.mod_case_notes(case_id=case.board_id, new_notes=notes)
    return await ctx.reply(f"Notes for case {case.board_id} updated.")
