"""
HalpyBOT v1.5

drill.py - Commands for the training and drilling of Seals

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
from typing import List
import logging

from ..packages.command import Commands, get_help_text
from ..packages.checks import Require, Drilled
from ..packages.models import Context
from ..packages.edsm import checklandmarks, EDSMLookupError, checkdssa, sys_cleaner
logger = logging.getLogger(__name__)

CacheOverride = False
cardinal_flip = {"North": "South", "NE": "SW", "East": "West", "SE": "NW",
                 "South": "North", "SW": "NE", "West": "East", "NW": "SE"}


@Commands.command("drillcase")
@Require.permission(Drilled)
@Require.channel()
async def cmd_drillcase(ctx: Context, args: List[str]):
    """
    Manually create a new drill case, separated by Commas

    Usage: !drillcase [cmdr], [platform], [system], [hull]
    Aliases: N/A
    """
    args = " ".join(args)
    args = args.split(",")
    if len(args) < 4:
        return await ctx.reply(get_help_text("drillcase"))
    system = await sys_cleaner(args[2])
    logging.critical(system)
    await ctx.reply(f"xxxx DRILL -- DRILL -- DRILL xxxx\n"
                    f"CMDR: {args[0]} -- Platform: {args[1]}\n"
                    f"System: {system} -- Hull: {args[3]}\n"
                    f"xxxxxxxx")
    await ctx.reply(await location(system))


@Commands.command("drillkfcase")
@Require.permission(Drilled)
@Require.channel()
async def cmd_drillkfcase(ctx: Context, args: List[str]):
    """
    Manually create a new drill case, separated by Commas

    Usage: !drillkfcase [cmdr], [platform], [system], [planet], [coords], [type]
    Aliases: N/A
    """
    args = " ".join(args)
    args = args.split(",")
    if len(args) < 6:
        return await ctx.reply(get_help_text("drillkfcase"))

    system = await sys_cleaner(args[2])
    logging.critical(system)
    await ctx.reply(f"xxxx DRILL -- DRILL -- DRILL xxxx\n"
                    f"CMDR: {args[0]} -- Platform: {args[1]}\n"
                    f"System: {system} -- Planet: {args[3]}\n"
                    f"Coordinates: {args[4]}\n:"
                    f"Type: {args[5]}\n"
                    f"xxxxxxxx")
    await ctx.reply(await location(system))


@Commands.command("drillcbcase")
@Require.permission(Drilled)
@Require.channel()
async def cmd_drillcbcase(ctx: Context, args: List[str]):
    """
    Manually create a new CB drill case, separated by Commas

    Usage: !drillcbcase [cmdr], [platform], [system], [hull], [cansynth], [o2]
    Aliases: N/A
    """
    args = " ".join(args)
    args = args.split(",")
    if len(args) < 6:
        return await ctx.reply(get_help_text("drillcbcase"))
    system = await sys_cleaner(args[2])
    logging.critical(system)
    await ctx.reply(f"xxxx DRILL -- DRILL -- DRILL xxxx\n"
                    f"CMDR: {args[0]} -- Platform: {args[1]}\n"
                    f"System: {system} -- Hull: {args[3]}\n"
                    f"Can Synth: {args[4]} -- O2 Timer: {args[5]}\n"
                    f"xxxxxxxx")
    await ctx.reply(await location(system))


async def location(system):
    # For now, we'll just use the Landmark system instead of replicating the whole announcement process
    # We can mask some of it to look identical.
    # TODO: This does not fully implement the system correction module. This should be done later. ~ Rixxan
    try:
        landmark, distance, direction = await checklandmarks(SysName=system, CacheOverride=CacheOverride)
        direction = cardinal_flip[direction]
        return f"System Exists in EDSM, {distance} LY {direction} of {landmark}."
    except EDSMLookupError as er:
        if str(er) == f"No major landmark systems within 10,000 ly of {system}.":
            dssa, distance, direction = await checkdssa(SysName=system, CacheOverride=CacheOverride)
            return f"{er}\nThe closest DSSA Carrier is in {dssa}, {distance} LY {direction} of"\
                   f"{await sys_cleaner(system)}."
        return str(er)
