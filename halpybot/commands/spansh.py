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
from ..packages.edsm import Commander
from ..packages.exceptions import EDSMLookupError
from ..packages.utils import spansh, dist_exceptions, sys_cleaner
from ..packages.command import Commands
from ..packages.models import Context, Case
from ..packages.case import get_case


@Commands.command("spansh")
@dist_exceptions
async def cmd_spansh(ctx: Context, args: List[str], cache_override):
    """
    Returns jump counts from sysA to sysB with a given jump range

    Usage: !spansh <--new> [system/cmdr 1] : [system/cmdr 2] : [jump range (Optional)]
    Aliases: n/a
    """
    try:
        # Parse systems/CMDRs from string
        list_to_str = " ".join([str(elem) for elem in args])
        points = list_to_str.split(":")
        pointa, pointb = "".join(points[0]).strip(), "".join(points[1]).strip()
    except IndexError:
        return await ctx.reply("Please provide two points to look up, separated by a :")
    if not pointb:
        return await ctx.reply("Please provide two points to look up, separated by a :")

    # In the event that a given point is actually a case (ID or CMDR)...
    try:
        case: Case = await get_case(ctx, pointa)
        pointa = case.system
    except KeyError:
        pass
    try:
        case: Case = await get_case(ctx, pointb)
        pointb = case.system
    except KeyError:
        pass

    try:
        # Check if PointA is CMDR
        loc_a = await Commander.location(name=pointa)
        if loc_a and loc_a.system is not None:
            pointa = await sys_cleaner(loc_a.system)
        loc_b = await Commander.location(name=pointb)
        if loc_b and loc_b.system is not None:
            pointb = await sys_cleaner(loc_b.system)
    except EDSMLookupError:
        logger.warning("EDSM appears to be down! Trying to continue regardless...")
        await ctx.reply("Warning! EDSM appears to be down. Trying to continue.")
        pass

    # Now, Format Jump Range And Send It
    try:
        jump_range = float(re.sub("(?i)LY", "", "".join(points[2])).strip())
    except ValueError:
        return await ctx.reply(
            "The Jump Range must be given as digits with an optional jump range."
        )

    logger.info(
        f"{ctx.sender} requested jumps counts from {pointa} to {pointb} with {jump_range}LY range"
    )
    return await spansh(ctx, jump_range, pointa, pointb)
