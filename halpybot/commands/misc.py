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
from ..packages.utils import shorten
from ..packages.checks import Require, Drilled
from ..packages.command import Commands, get_help_text
from ..packages.models import Context


@Commands.command("shorten")
@Require.permission(Drilled)
async def cmd_shorten(ctx: Context, args: List[str]):
    """
    Shorten a given URL with the configured YOURLS API

    Usage: !shorten [url]
    Aliases: n/a
    """
    if not args:
        return await ctx.reply(get_help_text("shorten"))
    logger.info(f"{ctx.sender} requested shortening of {args[0]}")
    surl = await shorten(args[0])
    return await ctx.reply(f"{ctx.sender}: Here's your short URL: {surl}")


@Commands.command("roll")
async def cmd_roll(ctx: Context, args: List[str]):
    """
    Roll the dice!

    Usage: !roll #d#
    Aliases: n/a
    """
    if not args:
        return await ctx.reply(get_help_text("roll"))
    dicesearch = re.search(r"^\d+d\d+$", args[0])
    if dicesearch is not None:
        dice = args[0].split("d")
        if int(dice[0]) > 10:
            return await ctx.reply("Can't roll more than 10 dice at a time!")
        rolls = []
        for roll in range(int(dice[0])):
            dice_roll = random.randint(1, int(dice[1]))
            rolls.append(dice_roll)
        total = sum(rolls)
        return await ctx.reply(f"{ctx.sender}: {total} ({str(rolls)})")
    return await ctx.reply(get_help_text("roll"))
