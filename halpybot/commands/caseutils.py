"""
caseutils.py - Commands involving the management of Seal cases

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
import re
from typing import List
from pendulum import now
from halpybot import config
from ..packages.command import Commands, get_help_text
from ..packages.edsm import (
    sys_cleaner,
    checklandmarks,
    NoResultsEDSM,
    EDSMConnectionError,
)
from ..packages.models import (
    Context,
    User,
    NoUserFound,
    Case,
    Status,
    CaseType,
    Platform,
    KFCoords,
    KFType,
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

    Usage: !listboard [Platform or Case Type]
    Aliases: n/a
    """
    # Get the Case Board
    caseboard = ctx.bot.board.by_id
    if not caseboard:
        return await ctx.redirect("The case board is empty!")
    # Process Args (If Exist)
    if args:
        platforms = [
            member.name.casefold().replace("_horizons", "") for member in Platform
        ]
        casetypes = [member.name.casefold() for member in CaseType]
        list_filter = args[0].casefold()
        if list_filter not in casetypes and list_filter not in platforms:
            list_filter = None
    else:
        list_filter = None

    filtered_cases = [
        case
        for case in caseboard.values()
        if (not list_filter)
        or (
            list_filter
            in (
                case.platform.name.casefold().replace("_horizons", ""),
                case.case_type.name.casefold(),
            )
        )
    ]

    message = "Here's the current case board:\n\n"
    for case in filtered_cases:
        hskf = (
            "Seal"
            if case.case_type in (CaseType.SEAL, CaseType.BLUE, CaseType.BLACK)
            else "Fisher"
            if case.case_type == CaseType.FISH
            else "Unknown"
        )
        long_ago = now(tz="utc").diff(case.updated_time).in_words()
        plt = case.platform.name.replace("_", " ")
        message += (
            f"Case {case.board_id}: Client: {case.client_name}, Platform: {plt}, "
            f"Type: {hskf}, Status: {case.status.name}, Updated: {long_ago} ago.\n"
        )

    message += f"\n{len(caseboard)} Cases on the Board."
    if list_filter:
        message += (
            f" Showing {len(filtered_cases)} that match(es) the filter {list_filter!r}."
        )
    return await ctx.redirect(message)


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
        await ctx.reply(update)
    try:
        landmark, distance, direction = await checklandmarks(newsys)
    except (NoResultsEDSM, EDSMConnectionError):
        return await ctx.reply(
            f"{newsys} not found in EDSM or unable to connect to EDSM."
        )
    return await ctx.reply(
        f"The closest landmark system is {landmark}, {distance} LY {direction} of {newsys}."
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

    Usage: !changetype [board ID] [new type]
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


@Commands.command("planet")
@Require.permission(Drilled)
@Require.channel()
async def cmd_planet(ctx: Context, args: List[str]):
    """
    Change the planet of an active KF case

    Usage: !planet [board ID] [new system]
    Aliases: n/a
    """
    if len(args) < 2:
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, "planet"))
    try:
        case: Case = await get_case(ctx, args[0])
    except KeyError:
        return await ctx.reply(f"No case found for {args[0]!r}.")
    if case.case_type != CaseType.FISH:
        return await ctx.reply("Planet can't be changed for non-Fisher case")
    newplan = await sys_cleaner(" ".join(args[1:]))
    update = await update_single_elem_case_prep(
        ctx=ctx, case=case, action="Client Planet", new_key="planet", new_item=newplan
    )
    if update:
        return await ctx.reply(update)


@Commands.command("casecoords")
@Require.permission(Drilled)
@Require.channel()
async def cmd_coords(ctx: Context, args: List[str]):
    """
    Change the coords of an active KF case

    Usage: !casecoords [board ID] [X Coordinate Float] [Y Coordinate Float]
    Aliases: n/a
    """
    if len(args) < 2:
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, "casecoords"))
    try:
        case: Case = await get_case(ctx, args[0])
    except KeyError:
        return await ctx.reply(f"No case found for {args[0]!r}.")
    if case.case_type != CaseType.FISH:
        return await ctx.reply("Coordinates can't be changed for non-Fisher case")
    try:
        xcoord = float(args[1].strip())
        ycoord = float(args[2].strip())
    except ValueError as val_err:
        raise ValueError("KF Coordinates Improperly Formatted") from val_err
    newcoords = KFCoords(xcoord, ycoord)
    update = await update_single_elem_case_prep(
        ctx=ctx,
        case=case,
        action="Client Coordinates",
        new_key="pcoords",
        new_item=newcoords,
    )
    if update:
        return await ctx.reply(update)


@Commands.command("o2time")
@Require.permission(Drilled)
@Require.channel()
async def cmd_oxtime(ctx: Context, args: List[str]):
    """
    Change the remaining oxygen timer for a case

    Usage: !o2time [board ID] [O2 Time in NN:NN]
    Aliases: n/a
    """
    if len(args) < 2:
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, "o2time"))
    try:
        case: Case = await get_case(ctx, args[0])
    except KeyError:
        return await ctx.reply(f"No case found for {args[0]!r}.")
    if case.case_type not in (CaseType.BLACK, CaseType.BLUE):
        return await ctx.reply("O2 Timer Irrelevant - Canopy Not Breached.")
    pattern = r"^\d{2}:\d{2}$"
    if not re.match(pattern, args[2].strip()):
        return await ctx.reply("Invalid O2 Time Given. Does not match pattern ##:##.")
    update = await update_single_elem_case_prep(
        ctx=ctx,
        case=case,
        action="O2 Timer",
        new_key="o2_timer",
        new_item=args[1].strip(),
    )
    if update:
        return await ctx.reply(update)


@Commands.command("synth")
@Require.permission(Drilled)
@Require.channel()
async def cmd_synth(ctx: Context, args: List[str]):
    """
    Toggle if a CMDR has synths available for a given case.

    Usage: !synth [board ID] [Yes/True/No/False]
    Aliases: n/a
    """
    if len(args) < 2:
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, "synth"))
    try:
        case: Case = await get_case(ctx, args[0])
    except KeyError:
        return await ctx.reply(f"No case found for {args[0]!r}.")
    if args[1].casefold() in ("yes", "true"):
        new_synth = True
    elif args[1].casefold() in ("no", "false"):
        new_synth = False
    else:
        return await ctx.reply("Invalid synth ability given.")
    if new_synth == case.can_synth:
        return await ctx.reply(f"Synth available already set to {new_synth}")
    update = await update_single_elem_case_prep(
        ctx=ctx,
        case=case,
        action="Synth Status",
        new_key="can_synth",
        new_item=new_synth,
    )
    if update:
        return await ctx.reply(update)


@Commands.command("kftype")
@Require.permission(Drilled)
@Require.channel()
async def cmd_changetype(ctx: Context, args: List[str]):
    """
    Change the case type between KF subtypes.

    Usage: !kftype [board ID] [new type]
    Aliases: n/a

    LIFT = 0
    GOLF = 1
    PUCK = 2
    PICK = 3
    """
    if len(args) < 2:
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, "kftype"))
    try:
        case: Case = await get_case(ctx, args[0])
    except KeyError:
        return await ctx.reply(f"No case found for {args[0]!r}.")
    if case.case_type != CaseType.FISH:
        return await ctx.reply("KFType can't be changed for non-Fisher case")
    potential_type = args[1].casefold()
    try:
        new_type = getattr(KFType, potential_type.upper())
    except AttributeError:
        return await ctx.reply("Invalid New KF Subtype Given.")
    update = await update_single_elem_case_prep(
        ctx=ctx,
        case=case,
        action="Kingfisher Type",
        new_key="kftype",
        new_item=new_type,
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
        # Human Indexes Start at 1. Translate it to proper array.
        del_index = int(args[1]) - 1
        target_line = case.case_notes[del_index]
    except (ValueError, IndexError):
        return await ctx.reply("Invalid Note Index provided!")
    await ctx.reply(f"Removing line {target_line!r}")
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
        # Human Indexes Start at 1. Translate it to proper array.
        note_index = int(args[1]) - 1
        target_line = case.case_notes[note_index]
    except (ValueError, IndexError):
        return await ctx.reply("Invalid Note Index provided!")
    await ctx.reply(f"Editing line {target_line!r} to the provided text.")
    notes: List[str] = case.case_notes
    notes[note_index] = f"{' '.join(args[2:])} - {ctx.sender} ({now(tz='UTC')})"
    await ctx.bot.board.mod_case_notes(case_id=case.board_id, new_notes=notes)
    return await ctx.reply(f"Notes for case {case.board_id} updated.")
