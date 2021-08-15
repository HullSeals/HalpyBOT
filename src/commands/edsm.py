"""
HalpyBOT v1.5

edsm.py - EDSM Interface commands

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List

from ..packages.edsm import (GalaxySystem, Commander, EDSMLookupError,
                             EDSMConnectionError, checkdistance, checklandmarks,
                             checkdssa)
from ..packages.command import Commands
from ..packages.models import Context


@Commands.command("lookup", "syslookup")
async def cmd_systemlookup(ctx: Context, args: List[str]):
    """
    Check EDSM for the existence of a system.

    Usage: !lookup <--new> [system name]
    Aliases: syslookup
    """

    # Input validation
    if not args:
        return await ctx.reply("No system given! Please provide a system name.")

    CacheOverride = False
    if args[0] == "--new":
        CacheOverride = True
        del args[0]

    system = ' '.join(args[0:]).strip()

    try:
        if await GalaxySystem.exists(name=system, CacheOverride=CacheOverride):
            return await ctx.reply(f"System {system} exists in EDSM")
        else:
            return await ctx.reply(f"System {system} not found in EDSM")

    except EDSMLookupError as er:
        return await ctx.reply(str(er))  # Return error if one is raised down the call stack.


@Commands.command("locatecmdr", "cmdrlookup", "locate")
async def cmd_cmdrlocate(ctx: Context, args: List[str]):
    """
    Check EDSM for the existence and location of a CMDR.

    Usage: !locatecmdr <--new> [cmdr name]
    Aliases: cmdrlookup, locate
    """

    # Input validation
    if not args:
        return await ctx.reply("No arguments given! Please provide a CMDR name.")

    CacheOverride = False
    if args[0] == "--new":
        CacheOverride = True
        del args[0]

    cmdr = ' '.join(args[0:]).strip()

    try:
        location = await Commander.location(name=cmdr, CacheOverride=CacheOverride)
    except EDSMConnectionError as er:
        return await ctx.reply(str(er))

    if location is None:
        return await ctx.reply("CMDR not found or not sharing location on EDSM")
    else:
        return await ctx.reply(f"CMDR {cmdr} was last seen in {location.system} on {location.time}")


@Commands.command("distance", "dist")
async def cmd_distlookup(ctx: Context, args: List[str]):
    """
    Check EDSM for the distance between two known points.

    Usage: !distance <--new> [system/cmdr 1] : [system/cmdr 2]
    Aliases: dist
    """

    # Input validation
    if not args:
        return await ctx.reply("Please provide two points to look up, separated by a :")

    CacheOverride = False
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
            distance, direction = await checkdistance(pointa, pointb, CacheOverride=CacheOverride)
        except EDSMLookupError as er:
            return await ctx.reply(str(er))
        return await ctx.reply(f"{pointa} is {distance} LY {direction} of {pointb}.")


@Commands.command("landmark")
async def cmd_landmarklookup(ctx: Context, args: List[str]):
    """
    Calculate the closest landmark system to a known EDSM system.

    Usage: !landmark [system/cmdr]
    Aliases: n/a
    """

    CacheOverride = False

    # Input validation
    if not args[0]:
        return await ctx.reply("No arguments given! Please provide a System or CMDR name.")

    if args[0] == "--new":
        CacheOverride = True
        del args[0]

    system = ctx.message.strip()

    try:
        landmark, distance, direction = await checklandmarks(SysName=system, CacheOverride=CacheOverride)
        return await ctx.reply(f"The closest landmark system is {landmark}, {distance} LY {direction} of {system}.")
    except EDSMLookupError as er:
        return await ctx.reply(str(er))


@Commands.command("dssa")
async def cmd_dssalookup(ctx: Context, args: List[str]):
    """
    Calculate the closest DSSA Carrier to a known EDSM system.

    Usage: !dssa [system/cmdr]
    Aliases: n/a
    File Last Updated: 2021-03-22 w/ 93 Carrier
    """

    CacheOverride = False

    # Input validation
    if not args[0]:
        return await ctx.reply("No arguments given! Please provide a System or CMDR name.")

    if args[0] == "--new":
        CacheOverride = True
        del args[0]

    system = ctx.message.strip()

    try:
        dssa, distance, direction = await checkdssa(SysName=system, CacheOverride=CacheOverride)
        return await ctx.reply(f"The closest DSSA Carrier is in {dssa}, {distance} LY {direction} of {system}.")
    except EDSMLookupError as er:
        return await ctx.reply(str(er))


@Commands.command("coordcheck", "coords")
async def cmd_coordslookup(ctx, args: List[str]):
    """
    Check EDSM for a nearby EDSM known system to a set of coordinates.

    Usage: !coords [x] [y] [z]
    Aliases: coords
    """

    # Input validation
    if not args:
        return await ctx.reply("No system given! Please provide a system name.")

    xcoord = args[0].strip()
    ycoord = args[1].strip()
    zcoord = args[2].strip()

    try:
        system, dist = await GalaxySystem.get_nearby(x=xcoord, y=ycoord, z=zcoord)
    except EDSMLookupError as er:
        return await ctx.reply(str(er))  # Return error if one is raised down the call stack.
    if system is None:
        return await ctx.reply(f"No systems known to EDSM within 100ly of {xcoord}, {ycoord}, {zcoord}.")
    else:
        return await ctx.reply(f"{system} is {dist} LY from {xcoord}, {ycoord}, {zcoord}.")