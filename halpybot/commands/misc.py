"""
misc.py - Miscellaneous Bot Functionality

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
import re
import random
from typing import List
from loguru import logger
import pendulum
from halpybot import config
from ..packages.utils import shorten, spansh, sys_cleaner
from ..packages.checks import Drilled, Pup, needs_permission
from ..packages.command import Commands, get_help_text
from ..packages.models import Context, Case
from ..packages.case import get_case
from ..packages.edsm import Commander


@Commands.command("shorten")
@needs_permission(Drilled)
async def cmd_shorten(ctx: Context, args: List[str]):
    """
    Shorten a given URL with the configured YOURLS API

    Usage: !shorten [url]
    Aliases: n/a
    """
    if not args:
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, "shorten"))
    if not config.yourls.enabled:
        return await ctx.reply("Unable to comply. YOURLS module not enabled.")
    logger.info(f"{ctx.sender} requested shortening of {args[0]}")
    surl = await shorten(args[0])
    return await ctx.reply(f"{ctx.sender}: Here's your short URL: {surl}")


@Commands.command("spansh")
@needs_permission(Drilled)
async def cmd_spansh(ctx: Context, args: List[str]):
    """
    Returns jump counts from sysA to sysB with a given jump range

    Usage: !spansh [jump range] [sysA] : [sysB]
    Aliases: n/a
    """
    if not args:
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, "spansh"))
    range = re.sub("(?i)LY", "", args.pop(0).replace(",", "."))
    if args[0] in ["LY", "Ly", "lY", "ly"]:
        args.pop(0)
    try:
        float(range)
    except ValueError:
        return await ctx.reply(
            "Please provide a jump range followed by two systems separated by a :"
        )
    try:
        list_to_str = " ".join([str(elem) for elem in args])
        points = list_to_str.split(":", 1)
        sysa, sysb = "".join(points[0]).strip(), "".join(points[1]).strip()
        sysa_text = await sys_cleaner(sysa)
        sysb_text = await sys_cleaner(sysb)
    except IndexError:
        return await ctx.reply(
            "Please provide a jump range followed by two systems separated by a :"
        )
    if not sysb:
        return await ctx.reply(
            "Please provide a jump range followed by two systems separated by a :"
        )
    try:  # Assume sysa is actually a CMDR, check if they exit and share their location
        cmdr = await Commander.location(name=sysa)
        if cmdr.system is not None:
            sysa = await sys_cleaner(cmdr.system)
            sysa_text = f"{sysa_text} (in {sysa})"
    except:
        pass
    try:  # Assume sysb is actually a CMDR, check if they exit and share their location
        cmdr = await Commander.location(name=sysb)
        if cmdr.system is not None:
            sysb = await sys_cleaner(cmdr.system)
            sysb_text = f"{sysb_text} (in {sysb})"
    except:
        pass
    try:  # Assume sysa is actually a CaseID, check if that case exists and get its system
        case: Case = await get_case(ctx, sysa)
        sysa = await sys_cleaner(case.system)
        sysa_text = f"Case {case.board_id} ({case.client_name} in {sysa})"
    except KeyError:
        pass
    try:  # Assume sysb is actually a CaseID, check if that case exists and get its system
        case: Case = await get_case(ctx, sysb)
        sysb = await sys_cleaner(case.system)
        sysb_text = f"Case {case.board_id} ({case.client_name} in {sysb})"
    except KeyError:
        pass
    logger.info(
        f"{ctx.sender} requested jumps counts from {sysa_text} to {sysb_text} with {range}LY range"
    )
    return await spansh(ctx, range, sysa, sysb, sysa_text, sysb_text)


@Commands.command("roll")
async def cmd_roll(ctx: Context, args: List[str]):
    """
    Roll the dice!

    Usage: !roll #d#
    Aliases: n/a
    """
    if not args:
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, "roll"))
    dicesearch = re.search(r"^\d+d\d+$", args[0])
    if dicesearch is None:
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, "roll"))
    dice = args[0].split("d")
    if int(dice[0]) > 10:
        return await ctx.reply("Can't roll more than 10 dice at a time!")
    rolls = []
    for roll in range(int(dice[0])):
        dice_roll = random.randint(1, int(dice[1]))
        rolls.append(dice_roll)
    total = sum(rolls)
    return await ctx.reply(f"{ctx.sender}: {total} {str(rolls)}")


@Commands.command("fireball")
@needs_permission(Pup)
async def cmd_fireball(ctx: Context, args: List[str]):
    """
    FOR FIREBALL!

    Usage: !fireball
    Aliases: n/a
    """
    if not args:
        subject = "chat"
    else:
        subject = args[0]
    dice = ["8d6"]
    await ctx.reply(
        f"Kawoosh! {ctx.sender} cast a fireball on {subject}! Rolling for damage..."
    )
    return await cmd_roll(ctx, dice)


@Commands.command("last")
async def cmd_last(ctx: Context, args: List[str]):
    """
    Check the time since the last case

    Usage: !last
    Aliases: n/a
    """
    if ctx.bot.board.time_last_case is None:
        return await ctx.reply("There haven't been any cases since I last restarted.")
    now = pendulum.now(tz="utc")
    elapsed = now.diff(ctx.bot.board.time_last_case).in_words()
    return await ctx.reply(f"Last case was {elapsed} ago.")
