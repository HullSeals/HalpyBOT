"""
HalpyBOT v1.5.2

edsm.py - EDSM Interface commands

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List

from ..packages.edsm import (GalaxySystem, Commander, EDSMLookupError,
                             EDSMConnectionError, checkdistance, checklandmarks,
                             checkdssa, sys_cleaner)
from ..packages.command import Commands, get_help_text
from ..packages.models import Context


@Commands.command("lookup", "syslookup")
async def cmd_systemlookup(ctx: Context, args: List[str]):
    """
    Check EDSM for the existence of a system.

    Usage: !lookup <--new> [system name]
    Aliases: syslookup
    """

    if len(args) == 0:
        return await ctx.reply(get_help_text("lookup"))
    cache_override = False
    if args[0] == "--new":
        cache_override = True
        del args[0]

    # For whoever find's this note, you're not crazy. arg[0:] == arg. You get a gold star
    # Gitblame means no gold star for Rik
    system = ' '.join(args[0:]).strip()

    try:
        if await GalaxySystem.exists(name=system, cache_override=cache_override):
            return await ctx.reply(f"System {await sys_cleaner(system)} exists in EDSM")
        else:
            return await ctx.reply(f"System {await sys_cleaner(system)} not found in EDSM")

    except EDSMLookupError as er:
        return await ctx.reply(str(er))  # Return error if one is raised down the call stack.


@Commands.command("locatecmdr", "cmdrlookup", "locate")
async def cmd_cmdrlocate(ctx: Context, args: List[str]):
    """
    Check EDSM for the existence and location of a CMDR.

    Usage: !locatecmdr <--new> [cmdr name]
    Aliases: cmdrlookup, locate
    """

    if len(args) == 0:
        return await ctx.reply(get_help_text("locatecmdr"))
    cache_override = False
    if args[0] == "--new":
        cache_override = True
        del args[0]

    # No. Only 1 gold star per stupid thing
    cmdr = ' '.join(args[0:]).strip()

    try:
        location = await Commander.location(name=cmdr, cache_override=cache_override)
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
    if len(args) == 0 or len(args) == 1:  # Minimum Number of Args is 2.
        return await ctx.reply(get_help_text("dist"))
    cache_override = False
    if args[0] == "--new":
        cache_override = True
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
            distance, direction = await checkdistance(pointa, pointb, cache_override=cache_override)
        except EDSMLookupError as er:
            return await ctx.reply(str(er))
        return await ctx.reply(f"{await sys_cleaner(pointa)} is {distance} LY {direction} of "
                               f"{await sys_cleaner(pointb)}.")


@Commands.command("landmark")
async def cmd_landmarklookup(ctx: Context, args: List[str]):
    """
    Calculate the closest landmark system to a known EDSM system.

    Usage: !landmark <--new> [system/cmdr]
    Aliases: n/a
    """

    cache_override = False

    if len(args) == 0:
        return await ctx.reply(get_help_text("landmark"))
    if args[0] == "--new":
        cache_override = True
        del args[0]

    system = ctx.message.strip()

    try:
        landmark, distance, direction = await checklandmarks(edsm_sys_name=system, cache_override=cache_override)
        return await ctx.reply(f"The closest landmark system is {landmark}, {distance} LY {direction} of "
                               f"{await sys_cleaner(system)}.")
    except EDSMLookupError as er:
        if str(er) == f"No major landmark systems within 10,000 ly of {system}.":
            dssa, distance, direction = await checkdssa(edsm_sys_name=system, cache_override=cache_override)
            return await ctx.reply(f"{er}\nThe closest DSSA Carrier is in {dssa}, {distance} LY " 
                                   f"{direction} of {await sys_cleaner(system)}.")
        return await ctx.reply(str(er))


@Commands.command("dssa")
async def cmd_dssalookup(ctx: Context, args: List[str]):
    """
    Calculate the closest DSSA Carrier to a known EDSM system.

    Usage: !dssa <--new> [system/cmdr]
    Aliases: n/a
    File Last Updated: 2021-03-22 w/ 93 Carrier
    """

    cache_override = False

    if len(args) == 0:
        return await ctx.reply(get_help_text("dssa"))
    if args[0] == "--new":
        cache_override = True
        del args[0]

    system = ctx.message.strip()

    try:
        dssa, distance, direction = await checkdssa(edsm_sys_name=system, cache_override=cache_override)
        return await ctx.reply(f"The closest DSSA Carrier is in {dssa}, {distance} LY {direction} of "
                               f"{await sys_cleaner(system)}.")
    except EDSMLookupError as er:
        return await ctx.reply(str(er))


@Commands.command("coordcheck", "coords")
async def cmd_coordslookup(ctx, args: List[str]):
    """
    Check EDSM for a nearby EDSM known system to a set of coordinates.

    Usage: !coords [x] [y] [z]
    Aliases: coords
    """

    if len(args) == 0 or len(args) == 1 or len(args) == 2:  # Minimum Number of Args is 3.
        return await ctx.reply(get_help_text("coords"))
    xcoord = args[0].strip()
    ycoord = args[1].strip()
    zcoord = args[2].strip()
    try:
        coordcheck = float(xcoord)
        coordcheck = float(ycoord)
        coordcheck = float(zcoord)
    except ValueError:
        return await ctx.reply("All coordinates must be numeric.")
    try:
        system, dist = await GalaxySystem.get_nearby(x=xcoord, y=ycoord, z=zcoord)
    except EDSMLookupError as er:
        return await ctx.reply(str(er))  # Return error if one is raised down the call stack.
    if system is None:
        return await ctx.reply(f"No systems known to EDSM within 100ly of {xcoord}, {ycoord}, {zcoord}.")
    else:
        return await ctx.reply(f"{system} is {dist} LY from {xcoord}, {ycoord}, {zcoord}.")
