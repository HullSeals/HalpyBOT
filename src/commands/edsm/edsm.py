"""
HalpyBOT v1.2.3

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
    CacheOverride = False

    if args[0] == "--new":
        CacheOverride = True
        del args[0]

    system = ' '.join(args[0:]).strip()

    # Input validation
    if not system:
        return await ctx.reply("No system given! Please provide a system name.")

    try:
        if await GalaxySystem.exists(name=system, CacheOverride=CacheOverride):
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

    CacheOverride = False

    if args[0] == "--new":
        CacheOverride = True
        del args[0]

    cmdr = ' '.join(args[0:])  # TODO replace by ctx method
    cmdr = cmdr.strip()
    # Input validation
    if not cmdr:
        return await ctx.reply("No arguments given! Please provide a CMDR name.")

    try:
        location = await Commander.location(name=cmdr, CacheOverride=CacheOverride)
    except EDSMConnectionError as er:
        return await ctx.reply(str(er))

    if location is None:
        return await ctx.reply("CMDR not found or not sharing location on EDSM")
    else:
        return await ctx.reply(f"CMDR {cmdr} was last seen in {location.system} on {location.time}")


@Commands.command("distance", "dist")
async def cmd_distlookup(ctx, args: List[str]):
    """
    Check EDSM for the distance between two known points.

    Usage: !distance
    Aliases: dist
    """

    CacheOverride = False

    # Input validation
    if not args:
        return await ctx.reply("Please provide two points to look up, separated by a :")

    if args[0] == "--new":
        CacheOverride = True
        del args[0]

    try:
        # Parse systems/CMDRs from string
        listToStr = ' '.join([str(elem) for elem in args])
        points = listToStr.split(":", 1)
        pointa, pointb = ''.join(points[0]).strip(), ''.join(points[1]).strip()

    except IndexError:
        return await ctx.reply("Please provide two points to look up, separated by a :")

    if not pointb:
        return await ctx.reply("Please provide two points to look up, separated by a :")

    else:

        try:
            distance = await checkdistance(pointa, pointb, CacheOverride=CacheOverride)
        except EDSMLookupError as er:
            return await ctx.reply(str(er))
        return await ctx.reply(f"The distance between {pointa} and {pointb} is {distance} LY")


@Commands.command("landmark")
async def cmd_landmarklookup(ctx, args: List[str]):
    """
    Calculate the closest landmark system to a known EDSM system.

    Usage: !landmark
    Aliases: n/a
    """

    # Input validation
    if not args[0]:
        return await ctx.reply("No arguments given! Please provide a System or CMDR name.")
    system = ' '.join(args[0:])  # TODO replace by ctx method

    try:
        landmark, distance = await checklandmarks(SysName=system)
        return await ctx.reply(f"The closest landmark system is {landmark} at {distance} LY.")
    except EDSMLookupError as er:
        return await ctx.reply(str(er))
