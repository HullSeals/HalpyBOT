"""
spansh.py - Your GPS for the Neutron Highway!

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
import re
from typing import List
from loguru import logger
from halpybot import config
from .edsm import differentiate
from ..packages.edsm import Commander
from ..packages.exceptions import EDSMLookupError
from ..packages.utils import spansh, dist_exceptions, sys_cleaner
from ..packages.command import Commands, get_help_text
from ..packages.models import Context, Case
from ..packages.case import get_case


@Commands.command("spansh")
@dist_exceptions
async def cmd_spansh(ctx: Context, args: List[str], cache_override):
    """
    Returns jump counts from sysA to sysB with a given jump range

    Usage: !spansh <--new> [System/CMDR/caseID 1] : [System/CMDR/caseID 2] : [Jump Range]
    Aliases: n/a
    """
    if not config.spansh.enabled:
        return await ctx.reply("Unable to comply. SPANSH module not enabled.")

    points = await differentiate(ctx=ctx, args=args)
    if len(points) != 3:
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, ctx.command))
    try:
        # Check if PointA or PointB are CMDRs
        loc_a = await Commander.location(name=points[0][0])
        if loc_a and loc_a.system is not None:
            points[0][0] = await sys_cleaner(loc_a.system)
            points[0][1] = f"{points[0][1]} (in {points[0][0]})"
        loc_b = await Commander.location(name=points[1][0])
        if loc_b and loc_b.system is not None:
            points[1][0] = await sys_cleaner(loc_b.system)
            points[1][1] = f"{points[1][1]} (in {points[1][0]})"
    except EDSMLookupError:
        logger.warning("EDSM appears to be down! Trying to continue regardless...")
        await ctx.reply("Warning! EDSM appears to be down. Trying to continue.")
        pass

    # Now, Format Jump Range And Send It
    try:
        jump_range = float(re.sub("(?i)LY", "", "".join(points[2])).strip())
    except ValueError:
        return await ctx.reply(
            "The Jump Range must be given as digits with an optional decimal point."
        )
    if jump_range < 10 or jump_range > 150:
        return await ctx.reply("The Jump Range must be between 10 LY and 150 LY.")

    logger.info(
        f"{ctx.sender} requested jumps counts from {points[0][0]} to {points[1][0]} with {jump_range} LY range"
    )
    return await spansh(ctx, jump_range, points[0], points[1])
