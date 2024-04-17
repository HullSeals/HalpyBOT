"""
caseutils.py - Commands involving the management of Seal cases

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import re
from typing import List, Optional
from attr.converters import to_bool
from pendulum import now
from loguru import logger
from halpybot import config
from ..packages.exceptions import (
    NoUserFound,
    NoResultsEDSM,
    EDSMConnectionError,
    CaseAlreadyExists,
)
from ..packages.seals import whois
from ..packages.utils import (
    sys_cleaner,
    gather_case,
)
from ..packages.command import Commands
from ..packages.edsm import (
    checklandmarks,
)
from ..packages.models import (
    Context,
    User,
    Case,
    Status,
    CaseType,
    Platform,
    KFCoords,
    KFType,
    Seal,
)
from ..packages.checks import Drilled, Pup, needs_permission, in_channel, Admin
from ..packages.case import update_single_elem_case_prep, get_case


async def add_responder(ctx: Context, args: List[str], case: Case, resp_type: str):
    """Add a Responder to a given Case"""
    # Clean out the list, only pass "full" args.
    del args[0]
    args = [x.strip(" ") for x in args]
    args = [ele for ele in args if ele.strip()]

    # Current Responders:
    responders = getattr(case, resp_type)
    # Loop through the list, checking each to see if they are actually a user.
    for seal in args:
        if seal.endswith(",") or seal.endswith(":"):
            seal = seal[:-1]
        user_level = 1
        # AttributeError is thrown if a user does not exist. Accept and move on.
        try:
            chat_whois = await User.get_info(ctx.bot, str(seal))
            vhost = User.process_vhost(chat_whois.hostname)
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
        else:
            val_seal: Seal = await whois(ctx.bot.engine, str(seal))
            if val_seal not in responders:
                responders.append(val_seal)
    res_kwarg = {resp_type: responders}
    await ctx.bot.board.mod_case(case_id=case.board_id, **res_kwarg)


async def rem_responder(ctx: Context, args: List[str], case: Case, resp_type: str):
    """Remove a Responder from a given Case"""
    # Clean out the list, only pass "full" args.
    del args[0]
    args = [x.strip(" ") for x in args]
    args = [ele for ele in args if ele.strip()]

    # Current Responders:
    responders = getattr(case, resp_type)
    # Loop through the list, checking each to see if they are actually a user.
    for seal in args:
        if seal.endswith(",") or seal.endswith(":"):
            seal = seal[:-1]
        # AttributeError is thrown if a user does not exist. Accept and move on.
        try:
            val_seal: Seal = await whois(ctx.bot.engine, str(seal))
        except ValueError:
            continue
        if val_seal in responders:
            responders.remove(val_seal)
    res_kwarg = {resp_type: responders}
    await ctx.bot.board.mod_case(case_id=case.board_id, **res_kwarg)


# FACT WRAPPERS
@Commands.command("go")
@gather_case(2)
async def cmd_go(ctx: Context, args: List[str], case: Case):
    """
    Add an identified Seal as a responder to a case on the board.

    Usage: !go [Case ID] [seals]
    Aliases: n/a
    """
    await add_responder(ctx, args, case, resp_type="responders")
    return await ctx.reply(
        await ctx.bot.facts.fact_formatted(fact=("go", "en"), arguments=args)
    )


@Commands.command("welcome")
@needs_permission(Pup)
async def cmd_welcome(ctx: Context, args: List[str]):
    """
    Welcome the Client and add an identified Seal as a Dispatch responder.

    Usage: !welcome [Case ID]
    Aliases: n/a
    """
    case = None
    try:
        case: Optional[Case] = await get_case(ctx, args[0])
    except KeyError:
        for test_case in ctx.bot.board.by_id.values():
            if args[0].casefold() in test_case.irc_nick.casefold():
                case = test_case
                break
    if not case:
        await ctx.reply(
            await ctx.bot.facts.fact_formatted(fact=("welcome", "en"), arguments=args)
        )
        return await ctx.reply(f"Attn {ctx.sender}: Case for {args[0]} not found!")
    spatches = case.dispatchers
    try:
        spatch: Seal = await whois(ctx.bot.engine, ctx.sender)
    except ValueError as disp_no_exist:
        await ctx.reply(
            "Error! Dispatcher doesn't seem to exist in the database. Unable to comply."
        )
        raise ValueError from disp_no_exist
    if spatch not in spatches:
        spatches.append(spatch)
    res_kwarg = {"welcomed": True, "dispatchers": spatches}
    await ctx.bot.board.mod_case(case_id=case.board_id, **res_kwarg)
    args = [case.irc_nick]
    return await ctx.reply(
        await ctx.bot.facts.fact_formatted(fact=("welcome", "en"), arguments=args)
    )


# RESPONDER MANAGEMENT:
@Commands.command("addresp", "newseal")
@needs_permission(Drilled)
@in_channel
@gather_case(2)
async def cmd_addresp(ctx: Context, args: List[str], case: Case):
    """
    Add a new responder to a given case

    Usage: !addresp [board ID] [new responders]
    Aliases: n/a
    """
    await add_responder(ctx, args, case, resp_type="responders")
    return await ctx.reply(f"Responders for case {case.board_id} updated.")


@Commands.command("adddisp", "newspatch")
@needs_permission(Drilled)
@in_channel
@gather_case(2)
async def cmd_adddisp(ctx: Context, args: List[str], case: Case):
    """
    Add a new dispatcher to a given case

    Usage: !adddisp [board ID] [new dispatchers]
    Aliases: n/a
    """
    await add_responder(ctx, args, case, resp_type="dispatchers")
    return await ctx.reply(f"Dispatchers for case {case.board_id} updated.")


@Commands.command("remresp", "standdown", "stddn")
@needs_permission(Drilled)
@in_channel
@gather_case(2)
async def cmd_remresp(ctx: Context, args: List[str], case: Case):
    """
    Remove a responder from a given case

    Usage: !remresp [board ID] [new responders]
    Aliases: n/a
    """
    await rem_responder(ctx, args, case, resp_type="responders")
    return await ctx.reply(f"Responders for case {case.board_id} updated.")


@Commands.command("remdisp")
@needs_permission(Drilled)
@in_channel
@gather_case(2)
async def cmd_remdisp(ctx: Context, args: List[str], case: Case):
    """
    Remove a dispatcher from a given case

    Usage: !remdisp [board ID] [new dispatchers]
    Aliases: n/a
    """
    await rem_responder(ctx, args, case, resp_type="dispatchers")
    return await ctx.reply(f"Dispatchers for case {case.board_id} updated.")


# BOARD AND CASE LISTING
@Commands.command("listboard")
@needs_permission(Drilled)
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
    list_filter = args[0].casefold() if args else None
    hskf_by_type = {
        CaseType.SEAL: "Seal",
        CaseType.BLACK: "Seal",
        CaseType.BLUE: "Seal",
        CaseType.FISH: "Fisher",
    }
    count = 0
    message = "Here's the current case board:\n\n"
    for case in caseboard.values():
        if list_filter and list_filter not in (
            case.platform.name.casefold().replace("_horizons", ""),
            case.case_type.name.casefold(),
        ):
            continue
        hskf = hskf_by_type.get(case.case_type, "Unknown")
        long_ago = now(tz="utc").diff(case.updated_time).in_words()
        plt = case.platform.name.replace("_", " ")
        message += (
            f"Case {case.board_id}: Client: {case.client_name}, Platform: {plt}, "
            f"Type: {hskf}, Status: {case.status.name}, Updated: {long_ago} ago.\n"
        )
        count += 1

    message += f"\n{len(caseboard)} Cases on the Board."
    if list_filter:
        message += f" Showing {count} that match(es) the filter {list_filter!r}."
    if count == 0:
        message = f"No cases on the board that match the filter {list_filter!r}."
    return await ctx.redirect(message)


@Commands.command("listcase")
@needs_permission(Drilled)
@gather_case(1)
async def cmd_listcase(ctx: Context, args: List[str], case: Case):
    """
    Send a user the key details of a case on the board in DMs

    Usage: !listcase [board ID]
    Aliases: n/a
    """
    return await ctx.redirect(f"{case}")


# CASE MANAGEMENT
@Commands.command("rename")
@needs_permission(Drilled)
@in_channel
@gather_case(2)
async def cmd_renamecase(ctx: Context, args: List[str], case: Case):
    """
    Rename the user of an active case

    Usage: !rename [board ID] [new name]
    Aliases: n/a
    """
    try:
        await ctx.bot.board.rename_case(args[1], case, ctx.sender)
    except AssertionError as case_err:
        logger.warning(case_err)
        return await ctx.reply(f"Case Rename Failed. Names Match: {args[1]!r}")
    except CaseAlreadyExists as case_err:
        logger.warning(case_err)
        return await ctx.reply(f"A case already exists for the name {args[1]!r}")
    for channel in config.channels.rescue_channels:
        await ctx.bot.message(
            channel,
            f"Client for case {case.board_id} set to {args[1]!r} from {case.client_name!r}",
        )


@Commands.command("ircn")
@needs_permission(Drilled)
@in_channel
@gather_case(2)
async def cmd_ircn(ctx: Context, args: List[str], case: Case):
    """
    Rename the user of an active case

    Usage: !ircn [board ID] [valid IRC user]
    Aliases: n/a
    """
    try:
        await User.get_info(ctx.bot, args[1])
    except (AttributeError, NoUserFound):
        # Attribute Error thrown if user does not exist.
        return await ctx.reply("That's not an IRC user!")
    await update_single_elem_case_prep(
        ctx=ctx, case=case, action="IRC Name", new_key="irc_nick", new_item=args[1]
    )


@Commands.command("system")
@needs_permission(Drilled)
@in_channel
@gather_case(2)
async def cmd_system(ctx: Context, args: List[str], case: Case):
    """
    Change the system of an active case

    Usage: !rename [board ID] [new system]
    Aliases: n/a
    """
    newsys: str = " ".join(args[1:])
    newsys = await sys_cleaner(newsys)
    await update_single_elem_case_prep(
        ctx=ctx, case=case, action="Client System", new_key="system", new_item=newsys
    )
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
@needs_permission(Drilled)
@in_channel
@gather_case(2)
async def cmd_status(ctx: Context, args: List[str], case: Case):
    """
    Change the activity status of a case

    Usage: !status [board ID] [new status]
    Aliases: n/a
    """
    try:
        status = Status[args[1].upper()]
        if status == Status.CLOSED:
            return await ctx.reply(
                "Can't close a case with this command. Did you mean !close?"
            )
    except KeyError:
        return await ctx.reply("Invalid case status provided.")
    await update_single_elem_case_prep(
        ctx=ctx,
        case=case,
        action="Case Status",
        new_key="status",
        new_item=status,
        enum=True,
    )


@Commands.command("hull")
@needs_permission(Drilled)
@in_channel
@gather_case(2)
async def cmd_hull(ctx: Context, args: List[str], case: Case):
    """
    Change the starting hull percentage of a case

    Usage: !hull [board ID] [new hull %]
    Aliases: n/a
    """
    if case.case_type not in (CaseType.BLACK, CaseType.BLUE, CaseType.SEAL):
        return await ctx.reply("Hull can't be changed for non-Seal case")
    try:
        percent = int(args[1])
        if percent not in range(100):
            raise ValueError  # Mock a Value Error for invalid Hull Percentage
    except ValueError:
        return await ctx.reply(f"{args[1]!r} isn't a valid hull percentage")
    await update_single_elem_case_prep(
        ctx=ctx,
        case=case,
        action="Hull Percentage",
        new_key="hull_percent",
        new_item=percent,
    )


@Commands.command("changetype")
@needs_permission(Drilled)
@in_channel
@gather_case(2)
async def cmd_changetype(ctx: Context, args: List[str], case: Case):
    """
    Change the case type between Seal, KF, Black, or Blue.

    Usage: !changetype [board ID] [new type]
    Aliases: n/a

    SEAL = 1
    BLACK = 2
    BLUE = 3
    FISH = 4
    """
    potential_type = args[1].casefold()
    type_lookup = {
        "seal": CaseType.SEAL,
        "kf": CaseType.FISH,
        "fisher": CaseType.FISH,
        "fish": CaseType.FISH,
        "kingfish": CaseType.FISH,
        "kingfisher": CaseType.FISH,
        "blue": CaseType.BLUE,
        "black": CaseType.BLACK,
        "cb": CaseType.BLACK,
    }
    new_type = type_lookup.get(potential_type)
    if new_type is None:
        return await ctx.reply("Invalid New Case Type Given.")
    await update_single_elem_case_prep(
        ctx=ctx,
        case=case,
        action="Case Type",
        new_key="case_type",
        new_item=new_type,
        enum=True,
    )


@Commands.command("platform")
@needs_permission(Drilled)
@in_channel
@gather_case(2)
async def cmd_platform(ctx: Context, args: List[str], case: Case):
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
    platform_lookup = {
        "odyssey": Platform.ODYSSEY,
        "ody": Platform.ODYSSEY,
        "pc": Platform.ODYSSEY,
        "pc-o": Platform.ODYSSEY,
        "xbx": Platform.XBOX,
        "xb": Platform.XBOX,
        "xbox": Platform.XBOX,
        "ps4": Platform.PLAYSTATION,
        "ps": Platform.PLAYSTATION,
        "playstation": Platform.PLAYSTATION,
        "live": Platform.LIVE_HORIZONS,
        "horizons-live": Platform.LIVE_HORIZONS,
        "legacy": Platform.LEGACY_HORIZONS,
        "legacy-horizons": Platform.LEGACY_HORIZONS,
    }
    potential_plt = args[1].casefold()
    new_plt = platform_lookup.get(potential_plt)
    if new_plt is None:
        return await ctx.reply("Invalid New Case Type Given.")
    await update_single_elem_case_prep(
        ctx=ctx,
        case=case,
        action="Case Platform",
        new_key="platform",
        new_item=new_plt,
        enum=True,
    )


@Commands.command("planet")
@needs_permission(Drilled)
@in_channel
@gather_case(2)
async def cmd_planet(ctx: Context, args: List[str], case: Case):
    """
    Change the planet of an active KF case

    Usage: !planet [board ID] [new system]
    Aliases: n/a
    """
    if case.case_type != CaseType.FISH:
        return await ctx.reply("Planet can't be changed for non-Fisher case")
    newplan = await sys_cleaner(" ".join(args[1:]))
    await update_single_elem_case_prep(
        ctx=ctx, case=case, action="Client Planet", new_key="planet", new_item=newplan
    )


@Commands.command("casecoords")
@needs_permission(Drilled)
@in_channel
@gather_case(3)
async def cmd_coords(ctx: Context, args: List[str], case: Case):
    """
    Change the coords of an active KF case

    Usage: !casecoords [board ID] [X Coordinate Float] [Y Coordinate Float]
    Aliases: n/a
    """
    if case.case_type != CaseType.FISH:
        return await ctx.reply("Coordinates can't be changed for non-Fisher case")
    try:
        xcoord = float(args[1].strip())
        ycoord = float(args[2].strip())
    except ValueError as val_err:
        raise ValueError("KF Coordinates Improperly Formatted") from val_err
    newcoords = KFCoords(xcoord, ycoord)
    await update_single_elem_case_prep(
        ctx=ctx,
        case=case,
        action="Client Coordinates",
        new_key="pcoords",
        new_item=newcoords,
    )


@Commands.command("o2time")
@needs_permission(Drilled)
@in_channel
@gather_case(2)
async def cmd_oxtime(ctx: Context, args: List[str], case: Case):
    """
    Change the remaining oxygen timer for a case

    Usage: !o2time [board ID] [O2 Time in NN:NN]
    Aliases: n/a
    """
    if case.case_type not in (CaseType.BLACK, CaseType.BLUE):
        return await ctx.reply("O2 Timer Irrelevant - Canopy Not Breached.")
    pattern = r"^\d{2}:\d{2}$"
    if not re.match(pattern, args[2].strip()):
        return await ctx.reply("Invalid O2 Time Given. Does not match pattern ##:##.")
    await update_single_elem_case_prep(
        ctx=ctx,
        case=case,
        action="O2 Timer",
        new_key="o2_timer",
        new_item=args[1].strip(),
    )


@Commands.command("synth")
@needs_permission(Drilled)
@in_channel
@gather_case(2)
async def cmd_synth(ctx: Context, args: List[str], case: Case):
    """
    Toggle if a CMDR has synths available for a given case.

    Usage: !synth [board ID] [Yes/True/No/False]
    Aliases: n/a
    """
    try:
        new_stat = to_bool(args[1].casefold())
    except ValueError:
        return await ctx.reply("Invalid synth ability given.")
    if new_stat == case.can_synth:
        return await ctx.reply(f"Synth available already set to {new_stat}")
    await update_single_elem_case_prep(
        ctx=ctx,
        case=case,
        action="Synth Status",
        new_key="can_synth",
        new_item=new_stat,
    )


@Commands.command("canopy")
@needs_permission(Drilled)
@in_channel
@gather_case(2)
async def cmd_canopy(ctx: Context, args: List[str], case: Case):
    """
    Toggle if the canopy is broken for a given case.

    Usage: !canopy [board ID] [Yes/True/No/False]
    Aliases: n/a
    """
    # Gather Args
    try:
        canopy_broken = to_bool(args[1].casefold())
    except ValueError:
        if args[1].casefold() == "broken":
            canopy_broken = True
        elif args[1].casefold() == "intact":
            canopy_broken = False
        else:
            return await ctx.reply("Invalid Canopy Status given.")
    if case.case_type not in (CaseType.BLACK, CaseType.BLUE):
        return await ctx.reply("Canopy Status Can't Be Changed for Non-CB Cases!")
    await update_single_elem_case_prep(
        ctx=ctx,
        case=case,
        action="Canopy Status",
        new_key="canopy_broken",
        new_item=canopy_broken,
    )


@Commands.command("kftype")
@needs_permission(Drilled)
@in_channel
@gather_case(2)
async def cmd_changekftype(ctx: Context, args: List[str], case: Case):
    """
    Change the case type between KF subtypes.

    Usage: !kftype [board ID] [new type]
    Aliases: n/a

    LIFT = 0
    GOLF = 1
    PUCK = 2
    PICK = 3
    """
    if case.case_type != CaseType.FISH:
        return await ctx.reply("KFType can't be changed for non-Fisher case")
    potential_type = args[1].casefold()
    try:
        new_type = getattr(KFType, potential_type.upper())
    except AttributeError:
        return await ctx.reply("Invalid New KF Subtype Given.")
    await update_single_elem_case_prep(
        ctx=ctx,
        case=case,
        action="Kingfisher Type",
        new_key="kftype",
        new_item=new_type,
        enum=True,
    )


# NOTES MANAGEMENT
@Commands.command("notes", "updatenotes", "addnote")
@needs_permission(Drilled)
@gather_case(2)
async def cmd_notes(ctx: Context, args: List[str], case: Case):
    """
    Append a new entry to the Notes

    Usage: !notes [board ID] [new note line]
    Aliases: updatenotes, addnote
    """
    new_notes = (
        f"{' '.join(args[1:])} - {ctx.sender} ({now(tz='UTC').to_time_string()})"
    )
    case.case_notes.append(new_notes)
    return await ctx.reply(f"Notes for case {case.board_id} updated.")


@Commands.command("listnotes")
@needs_permission(Drilled)
@gather_case(1)
async def cmd_listnotes(ctx: Context, args: List[str], case: Case):
    """
    List out just the case notes to DMs

    Usage: !listnotes [board ID]
    Aliases: n/a
    """
    if not case.case_notes:
        return await ctx.reply(f"No Notes Found for case {case.board_id}")
    notes: str = ""
    for line_num, note in enumerate(case.case_notes, start=1):
        notes += f"{line_num}: {note}\n"
    return await ctx.redirect(notes)


@Commands.command("delnote")
@needs_permission(Drilled)
@in_channel
@gather_case(2)
async def cmd_delnote(ctx: Context, args: List[str], case: Case):
    """
    Delete a line of the notes for a given case

    Usage: !delnote [board ID] [note index]
    TODO: Can we get an "Are you sure?" check here?
    """
    if not case.case_notes:
        return await ctx.reply(f"No Notes Found for case {case.board_id}")
    try:
        # Human Indexes Start at 1. Translate it to proper array.
        del_index = int(args[1]) - 1
        target_line = case.case_notes[del_index]
    except (ValueError, IndexError):
        return await ctx.reply("Invalid Note Index provided!")
    await ctx.reply(f"Removing line {target_line!r}")
    del case.case_notes[del_index]
    return await ctx.reply(f"Notes for case {case.board_id} updated.")


@Commands.command("editnote")
@needs_permission(Drilled)
@in_channel
@gather_case(3)
async def cmd_editnote(ctx: Context, args: List[str], case: Case):
    """
    Alter a line of the notes for a given case

    Usage: !editnote [board ID] [note index] [new note content]
    TODO: Can we get an "Are you sure?" check here?
    """
    if not case.case_notes:
        return await ctx.reply(f"No Notes Found for case {case.board_id}")
    try:
        # Human Indexes Start at 1. Translate it to proper array.
        note_index = int(args[1]) - 1
        target_line = case.case_notes[note_index]
    except (ValueError, IndexError):
        return await ctx.reply("Invalid Note Index provided!")
    await ctx.reply(f"Editing line {target_line!r} to the provided text.")

    case.case_notes[note_index] = (
        f"{' '.join(args[2:])} - {ctx.sender} ({now(tz='UTC')})"
    )
    return await ctx.reply(f"Notes for case {case.board_id} updated.")


# ADMINSTRATIVE MANAGEMENT
@Commands.command("delcase", "remcase")
@needs_permission(Admin)
@in_channel
@gather_case(1)
async def cmd_remcase(ctx: Context, args: List[str], case: Case):
    """
    Removes a case from the board administratively, in case something screwed up.
    Not to be done lightly!

    Usage: !remcase [board ID]
    Aliases: delcase
    """
    if args:
        new_notes = (
            f"Admin Case Termination: {' '.join(args[1:])} - {ctx.sender}"
            f" ({now(tz='UTC').to_time_string()})"
        )
    else:
        new_notes = (
            f"{ctx.sender} administratively removed case {case.board_id} "
            f"from the board at {now(tz='UTC').to_time_string()}"
        )
    logger.warning(new_notes)
    case.case_notes.append(new_notes)
    await ctx.bot.board.del_case(case=case)
    return await ctx.reply(
        f"Administratively removed case {case.board_id} from the board."
    )
