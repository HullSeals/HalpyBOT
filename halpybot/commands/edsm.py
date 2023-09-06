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
from loguru import logger
from ..packages.edsm import (
    GalaxySystem,
    Commander,
    checkdistance,
    checklandmarks,
    checkdssa,
    diversions,
)
from ..packages.exceptions import NoNearbyEDSM, EDSMLookupError, DifferentiateArgsIssue
from ..packages.utils import (
    sys_cleaner,
    sys_exceptions,
    cmdr_exceptions,
    dist_exceptions,
    coords_exceptions,
)
from ..packages.command import Commands
from ..packages.models import Context, Case, Points, Point
from ..packages.case import get_case


async def differentiate(ctx: Context, args: List[str]) -> Points:
    """
    Differentiate if a given set of two systems are CMDRs, Cases, or Systems.

    Args:
        ctx (Context): The Bot Context
        args (List): A list of arguments from the bot.

    Returns:
        Points (Points): A Points object containing two Point objects and an optional Jump range

    Raises:
        DifferentiateArgsIssue: Arguments are malformed
    """
    # Parse System/CMDR/caseID from string
    list_to_str = " ".join([str(elem) for elem in args])
    list_points: List[str] = list_to_str.split(":")
    if len(list_points) < 2:
        await ctx.reply("Please provide two points to look up, separated by a :")
        raise DifferentiateArgsIssue
    point_a: Point = Point(list_points[0].strip())
    point_b: Point = Point(list_points[1].strip())
    points: Points = Points(point_a, point_b)

    if not point_a.name or not point_b.name:
        await ctx.reply("Please provide two points to look up, separated by a :")
        raise DifferentiateArgsIssue

    # Define Jump Count
    if len(list_points) == 3:
        try:
            points.jump_range = float(
                re.sub("(?i)LY", "", "".join(list_points[2])).strip()
            )
        except ValueError as val_err:
            # Jump Range must not be formatted correctly
            await ctx.reply(
                "The Jump Range must be given as digits with an optional decimal point."
            )
            raise DifferentiateArgsIssue from val_err
        if points.jump_range < 10 or points.jump_range > 500:
            # Jump Range has values that don't really make sense
            await ctx.reply("The Jump Range must be between 10 LY and 500 LY.")
            raise DifferentiateArgsIssue

    for point in [point_a, point_b]:
        # Check if Point is CaseID
        try:
            case: Case = await get_case(ctx, point.name)
            temp_point = case.system
            temp_pretty = f"Case {case.board_id} ({case.client_name} in {case.system})"
        except KeyError:
            temp_point = "".join(point.name).strip()
            temp_pretty = await sys_cleaner(point.name)
        # Check if point is CMDR
        try:
            loc_cmdr = await Commander.location(name=point.name)
            # Looks like CMDR's back on the menu, boys!
            if loc_cmdr and loc_cmdr.system is not None:
                temp_point = await sys_cleaner(loc_cmdr.system)
                temp_pretty = f"{await sys_cleaner(point.name)} (in {temp_point})"
        except EDSMLookupError:
            logger.warning("EDSM appears to be down! Trying to continue regardless...")
            await ctx.reply("Warning! EDSM appears to be down. Trying to continue.")
        point.name, point.pretty = temp_point, temp_pretty
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
    try:
        # Process provided arguments
        points: Points = await differentiate(ctx=ctx, args=args)
    except DifferentiateArgsIssue:
        # Arguments were malformed, user has already been informed, abort
        return await ctx.reply("Error encountered in Dist command, not continuing")

    distance, direction = await checkdistance(
        points.point_a.name, points.point_b.name, cache_override=cache_override
    )
    if not points.jump_range:  # No Jump Range given, respond with Distance
        return await ctx.reply(
            f"{points.point_a.pretty} is {distance} LY {direction} of "
            f"{points.point_b.pretty}."
        )
    # Jump Range given, calculate Jump Count and return Count and Distance
    jumps = math.ceil(float(distance.replace(",", "")) / points.jump_range)
    return await ctx.reply(
        f"{points.point_a.pretty} is {distance} LY (~{jumps} Jumps) {direction} of "
        f"{points.point_b.pretty}."
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
