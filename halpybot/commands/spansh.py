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

    Usage: !spansh <--new> [System/CMDR/caseID 1] : [System/CMDR/caseID 2] : [Jump Range]
    Aliases: n/a
    """
    if not config.spansh.enabled:
        return await ctx.reply("Unable to comply. SPANSH module not enabled.")
    try:
        # Parse systems/CMDRs/CaseIDs from string
        list_to_str = " ".join([str(elem) for elem in args])
        points = list_to_str.split(":")
        pointa, pointb = "".join(points[0]).strip(), "".join(points[1]).strip()
        pointa_pretty = await sys_cleaner(pointa)
        pointb_pretty = await sys_cleaner(pointb)
    except IndexError:
        return await ctx.reply("Please provide two points to look up, separated by a :")
    if not pointb:
        return await ctx.reply("Please provide two points to look up, separated by a :")

    # In the event that a given point is actually a case (ID or CMDR)...
    try:
        case: Case = await get_case(ctx, pointa)
        pointa = case.system
        pointa_pretty = f"Case {case.board_id} ({case.client_name} in {case.system})"
    except KeyError:
        pass
    try:
        case: Case = await get_case(ctx, pointb)
        pointb = case.system
        pointb_pretty = f"Case {case.board_id} ({case.client_name} in {case.system})"
    except KeyError:
        pass

    try:
        # Check if PointA or PointB are CMDRs
        loc_a = await Commander.location(name=pointa)
        if loc_a and loc_a.system is not None:
            pointa = await sys_cleaner(loc_a.system)
            pointa_pretty = f"{pointa_pretty} (in {pointa})"
        loc_b = await Commander.location(name=pointb)
        if loc_b and loc_b.system is not None:
            pointb = await sys_cleaner(loc_b.system)
            pointb_pretty = f"{pointb_pretty} (in {pointb})"
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
        f"{ctx.sender} requested jumps counts from {pointa} to {pointb} with {jump_range} LY range"
    )
    return await spansh(ctx, jump_range, pointa, pointb, pointa_pretty, pointb_pretty)
