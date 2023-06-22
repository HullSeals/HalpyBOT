"""
spansh.py - Your GPS for the Neutron Highway!

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
from typing import List
from loguru import logger
from halpybot import config
from .edsm import differentiate
from ..packages.exceptions import DifferentiateArgsIssue
from ..packages.utils import spansh, dist_exceptions
from ..packages.command import Commands, get_help_text
from ..packages.models import Context


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
    try:
        points = await differentiate(ctx=ctx, args=args)  # Process provided arguments
    except DifferentiateArgsIssue:
        # Arguments were malfirmed, user has already been informed, abort
        return
    if len(points) != 3:  # No Jump Range given
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, ctx.command))
    logger.info(
        f"{ctx.sender} requested jumps counts from {points[0][0]} to {points[1][0]} with {points[2]} LY range"
    )
    return await spansh(ctx, [points[0], points[1]], points[2])
