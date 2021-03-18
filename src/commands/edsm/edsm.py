"""
HalpyBOT v1.2.2

edsm.py - EDSM Interface commands

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List
from src.packages.edsm.edsm import *
from .. import Commands


@Commands.command("lookup", "syslookup")
async def cmd_systemlookup(ctx, args: List[str]):
    """
    Check EDSM for the existence of a system.

    Usage: !lookup
    Aliases: syslookup
    """
    system = ' '.join(args[0:])  # TODO replace by ctx method

    # Input validation
    if not system:
        return await ctx.reply("No system given! Please provide a system name.")

    try:
        if await system_exists(system):
            return await ctx.reply(f"System {system} exists in EDSM")
        else:
            return await ctx.reply(f"System {system} not found in EDSM")

    except EDSMLookupError as er:
        return await ctx.reply(str(er))  # Return error if one is raised down the call stack.


@Commands.command("locatecmdr", "cmdrlookup", "locate")
async def cmd_cmdrlocate(ctx, args: List[str]):
    """
    Check EDSM for the existence and location of a CMDR.

    Usage: !locatecmdr
    Aliases: cmdrlookup, locate
    """

    cmdr = ' '.join(args[0:])  # TODO replace by ctx method

    # Input validation
    if not cmdr:
        return await ctx.reply("No arguments given! Please provide a CMDR name.")

    try:
        system, date = await locatecmdr(cmdr)
    except EDSMLookupError as er:
        return await ctx.reply(str(er))

    return await ctx.reply(f"CMDR {cmdr} was last seen in {system} on {date}")


@Commands.command("distance", "dist")
async def cmd_distlookup(ctx, args: List[str]):
    """
    Check EDSM for the distance between two known points.

    Usage: !distance
    Aliases: dist
    """

    if not args:
        return await ctx.reply("Please provide two points to look up, separated by a :")
    try:
        listToStr = ' '.join([str(elem) for elem in args])
        points = listToStr.split(":", 1)
        pointa = ''.join(points[0]).strip()
        pointb = ''.join(points[1]).strip()
    except IndexError:
        return await ctx.reply("Please provide two points to look up, separated by a :")
    if not pointb:
        return await ctx.reply("Please provide two points to look up, separated by a :")
    else:
        try:
            return await ctx.reply(await checkdistance(pointa, pointb))
        except EDSMLookupError as er:
            return await ctx.reply(str(errors=er))
