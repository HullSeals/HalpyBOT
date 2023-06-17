"""
edsm.py - EDSM Interface commands

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
import math
import re
from typing import List
from ..packages.edsm import (
    GalaxySystem,
    Commander,
    checkdistance,
    checklandmarks,
    checkdssa,
    diversions,
)
from ..packages.exceptions import NoNearbyEDSM
from ..packages.utils import (
    sys_cleaner,
    sys_exceptions,
    cmdr_exceptions,
    dist_exceptions,
    coords_exceptions,
)
from ..packages.command import Commands
from ..packages.models import Context, Case
from ..packages.case import get_case


async def differentiate(ctx: Context, args: List[str]):
    """
    Differentiate if a given set of two systems are CMDRs, Cases, or Systems.

    Args:
        ctx (Context): The Bot Context
        args (List): A list of arguments from the bot.

    Returns:
        points (List): A List of points, in the format of:
         - two sub-lists with detailed and pretty information
         - an optional third Jump Range element.
    """
    try:
        # Parse systems/CMDRs from string
        list_to_str = " ".join([str(elem) for elem in args])
        points: List = list_to_str.split(":")
        points[0], points[1] = points[0].strip(), points[1].strip()
    except IndexError:
        return await ctx.reply("Please provide two points to look up, separated by a :")
    if len(points) < 2:
        return await ctx.reply("Please provide two points to look up, separated by a :")
    for i, point in enumerate(points):
        if i == 2:
            break
        try:  # Assume pointa is actually a CaseID, check if that case exists and get its system
            case: Case = await get_case(ctx, point)
            temp_point = case.system
            temp_pretty = f"Case {case.board_id} ({case.client_name} in {case.system})"
        except KeyError:  # Must not be a case, clean up and move along.
            temp_pretty = await sys_cleaner(point)
            temp_point = "".join(point).strip()
        points[i] = [temp_point, temp_pretty]
    return points


@Commands.command("lookup", "syslookup")
@sys_exceptions
async def cmd_systemlookup(ctx: Context, cleaned_sys, cache_override):
    """
    Check EDSM for the existence of a system.

    Usage: !lookup <--new> [system name]
    Aliases: syslookup
    """
    if await GalaxySystem.exists(name=cleaned_sys, cache_override=cache_override):
        return await ctx.reply(f"System {cleaned_sys} exists in EDSM")
    return await ctx.reply(f"System {cleaned_sys} not found in EDSM")


@Commands.command("locatecmdr", "cmdrlookup", "locate")
@cmdr_exceptions
async def cmd_cmdrlocate(ctx: Context, cmdr, cache_override):
    """
    Check EDSM for the existence and location of a CMDR.

    Usage: !locatecmdr <--new> [cmdr name]
    Aliases: cmdrlookup, locate
    """
    location = await Commander.location(name=cmdr, cache_override=cache_override)
    if location is None:
        return await ctx.reply("CMDR not found or not sharing location on EDSM")
    return await ctx.reply(
        f"CMDR {cmdr} was last seen in {location.system} on {location.time}"
    )


@Commands.command("distance", "dist")
@dist_exceptions
async def cmd_distlookup(ctx: Context, args: List[str], cache_override):
    """
    Check EDSM for the distance between two known points.

    Usage: !distance <--new> [System/CMDR/caseID 1] : [System/CMDR/caseID 2] : <Jump Range>
    Aliases: dist
    """
    points = await differentiate(ctx=ctx, args=args)
    distance, direction = await checkdistance(
        points[0][0], points[1][0], cache_override=cache_override
    )
    if len(points) < 3:
        return await ctx.reply(
            f"{points[0][1]} is {distance} LY {direction} of " f"{points[1][1]}."
        )
    try:
        jump_range = float(re.sub("(?i)LY", "", "".join(points[2])).strip())
        jumps = math.ceil(float(distance.replace(",", "")) / jump_range)
        if jump_range < 10 or jump_range > 500:
            return await ctx.reply("The Jump Range must be between 10 LY and 500 LY.")
        return await ctx.reply(
            f"{points[0][1]} is {distance} LY (~{jumps} Jumps) {direction} of "
            f"{points[1][1]}."
        )
    except ValueError:
        return await ctx.reply(
            "The Jump Range must be given as digits with an optional decimal point."
        )


@Commands.command("landmark")
@sys_exceptions
async def cmd_landmarklookup(ctx: Context, cleaned_sys, cache_override):
    """
    Calculate the closest landmark system to a known EDSM system.

    Usage: !landmark <--new> [system/cmdr]
    Aliases: n/a
    """
    try:
        landmark, distance, direction = await checklandmarks(
            edsm_sys_name=cleaned_sys, cache_override=cache_override
        )
        return await ctx.reply(
            f"The closest landmark system is {landmark}, {distance} LY {direction} of {cleaned_sys}."
        )
    except NoNearbyEDSM:
        dssa, distance, direction = await checkdssa(
            edsm_sys_name=cleaned_sys, cache_override=cache_override
        )
        return await ctx.reply(
            f"No major landmark systems within 10,000 LY of {cleaned_sys}.\n"
            f"The closest DSSA Carrier is in {dssa}, {distance} LY "
            f"{direction} of {cleaned_sys}."
        )


@Commands.command("dssa")
@sys_exceptions
async def cmd_dssalookup(ctx: Context, cleaned_sys, cache_override):
    """
    Calculate the closest DSSA Carrier to a known EDSM system.

    Usage: !dssa <--new> [system/cmdr]
    Aliases: n/a
    File Last Updated: 2021-03-22 w/ 93 Carrier
    """
    dssa, distance, direction = await checkdssa(
        edsm_sys_name=cleaned_sys, cache_override=cache_override
    )
    return await ctx.reply(
        f"The closest DSSA Carrier is in {dssa}, {distance} LY {direction} of "
        f"{cleaned_sys}."
    )


@Commands.command("coordcheck", "coords")
@coords_exceptions
async def cmd_coordslookup(ctx, xcoord, ycoord, zcoord):
    """
    Check EDSM for a nearby EDSM known system to a set of coordinates.

    Usage: !coords [x] [y] [z]
    Aliases: coords
    """
    system, dist = await GalaxySystem.get_nearby(
        x_coord=xcoord, y_coord=ycoord, z_coord=zcoord
    )
    if system is None:
        return await ctx.reply(
            f"No systems known to EDSM within 100ly of {xcoord}, {ycoord}, {zcoord}."
        )
    return await ctx.reply(f"{system} is {dist} LY from {xcoord}, {ycoord}, {zcoord}.")


@Commands.command("diversion")
@sys_exceptions
async def cmd_diversionlookup(ctx: Context, cleaned_sys, cache_override):
    """
    Calculate the 5 closest FDEV-placed structures with repair capability to a known EDSM location.

    Usage: !diversion <--new> [system/cmdr]
    Aliases: n/a
    File Last Updated: 2022-05-23 w/ 7,384 Qualified Stations
    """
    first, second, third, fourth, fifth = await diversions(
        edsm_sys_name=cleaned_sys, cache_override=cache_override
    )
    return await ctx.reply(
        f"Closest Diversion Stations to {cleaned_sys}:\n"
        f"1st: {first.name}, {float(first.item):,} LY {first.local_direction} in {first.system_name} "
        f"({first.dist_star} LS from entry)\n"
        f"2nd: {second.name}, {float(second.item):,} LY {second.local_direction} in {second.system_name} "
        f"({second.dist_star} LS from entry)\n"
        f"3rd: {third.name}, {float(third.item):,} LY {third.local_direction} in {third.system_name} "
        f"({third.dist_star} LS from entry)\n"
        f"4th: {fourth.name}, {float(fourth.item):,} LY {fourth.local_direction} in {fourth.system_name} "
        f"({fourth.dist_star} LS from entry)\n"
        f"5th: {fifth.name}, {float(fifth.item):,} LY {fifth.local_direction} in {fifth.system_name} "
        f"({fifth.dist_star} LS from entry)"
    )
