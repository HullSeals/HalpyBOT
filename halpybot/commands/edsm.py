"""
HalpyBOT v1.6

edsm.py - EDSM Interface commands

Copyright (c) 2022 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
from typing import List
from loguru import logger

from ..packages.edsm import (
    GalaxySystem,
    Commander,
    EDSMLookupError,
    EDSMConnectionError,
    checkdistance,
    checklandmarks,
    checkdssa,
    sys_cleaner,
    diversions,
    NoResultsEDSM,
)
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
    system = " ".join(args[0:]).strip()

    try:
        if await GalaxySystem.exists(name=system, cache_override=cache_override):
            return await ctx.reply(f"System {await sys_cleaner(system)} exists in EDSM")
        return await ctx.reply(f"System {await sys_cleaner(system)} not found in EDSM")
    except NoResultsEDSM:
        return await ctx.reply(
            f"No system named {system} was found in the EDSM database."
        )

    except EDSMLookupError:
        logger.exception("Failed to query EDSM for system details.")
        return await ctx.reply("Failed to query EDSM for system details.")


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
    cmdr = " ".join(args[0:]).strip()

    try:
        location = await Commander.location(name=cmdr, cache_override=cache_override)
    except NoResultsEDSM:
        return await ctx.reply(f"No CMDR named {cmdr} was found in the EDSM database.")
    except EDSMConnectionError:
        logger.exception("Failed to query EDSM for commander data.")
        # kill it. kill it with fire. ~ TheUnkn0wn1
        return await ctx.reply("Failed to query EDSM for commander data.")

    if location is None:
        return await ctx.reply("CMDR not found or not sharing location on EDSM")
    return await ctx.reply(
        f"CMDR {cmdr} was last seen in {location.system} on {location.time}"
    )


@Commands.command("distance", "dist")
async def cmd_distlookup(ctx: Context, args: List[str]):
    """
    Check EDSM for the distance between two known points.

    Usage: !distance <--new> [system/cmdr 1] : [system/cmdr 2]
    Aliases: dist
    """
    if len(args) <= 1:  # Minimum Number of Args is 2.
        return await ctx.reply(get_help_text("dist"))
    cache_override = False
    if args[0] == "--new":
        cache_override = True
        del args[0]

    try:
        # Parse systems/CMDRs from string
        list_to_str = " ".join([str(elem) for elem in args])
        points = list_to_str.split(":", 1)
        pointa, pointb = "".join(points[0]).strip(), "".join(points[1]).strip()

    except IndexError:
        return await ctx.reply("Please provide two points to look up, separated by a :")

    if not pointb:
        return await ctx.reply("Please provide two points to look up, separated by a :")
    try:
        distance, direction = await checkdistance(
            pointa, pointb, cache_override=cache_override
        )
    except NoResultsEDSM:
        return await ctx.reply(
            f"No system and/or commander was found in the EDSM database for one of the points."
        )
    except EDSMLookupError:
        logger.exception("Failed to query EDSM for system or CMDR details.")
        return await ctx.reply("Failed to query EDSM for system or CMDR details.")
    return await ctx.reply(
        f"{await sys_cleaner(pointa)} is {distance} LY {direction} of "
        f"{await sys_cleaner(pointb)}."
    )


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
        landmark, distance, direction = await checklandmarks(
            edsm_sys_name=system, cache_override=cache_override
        )
        return await ctx.reply(
            f"The closest landmark system is {landmark}, {distance} LY {direction} of "
            f"{await sys_cleaner(system)}."
        )
    except NoResultsEDSM:
        return await ctx.reply(
            f"No system and/or commander named {system} was found in the EDSM database."
        )
    except EDSMLookupError:
        if (
            str(EDSMLookupError)
            == f"No major landmark systems within 10,000 ly of {system}."
        ):
            dssa, distance, direction = await checkdssa(
                edsm_sys_name=system, cache_override=cache_override
            )
            return await ctx.reply(
                f"{EDSMLookupError}\nThe closest DSSA Carrier is in {dssa}, {distance} LY "
                f"{direction} of {await sys_cleaner(system)}."
            )
        logger.exception("Failed to query EDSM for landmark details.")
        return await ctx.reply("Failed to query EDSM for landmark details.")


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
        dssa, distance, direction = await checkdssa(
            edsm_sys_name=system, cache_override=cache_override
        )
        return await ctx.reply(
            f"The closest DSSA Carrier is in {dssa}, {distance} LY {direction} of "
            f"{await sys_cleaner(system)}."
        )
    except NoResultsEDSM:
        return await ctx.reply(
            f"No system and/or commander named {system} was found in the EDSM database."
        )
    except EDSMLookupError:
        logger.exception("Failed to query EDSM for DSSA details.")
        return await ctx.reply("Failed to query EDSM for DSSA details.")


@Commands.command("coordcheck", "coords")
async def cmd_coordslookup(ctx, args: List[str]):
    """
    Check EDSM for a nearby EDSM known system to a set of coordinates.

    Usage: !coords [x] [y] [z]
    Aliases: coords
    """

    if len(args) <= 2:  # Minimum Number of Args is 3.
        return await ctx.reply(get_help_text("coords"))
    xcoord = args[0].strip()
    ycoord = args[1].strip()
    zcoord = args[2].strip()
    try:
        float(xcoord)
        float(ycoord)
        float(zcoord)
    except ValueError:
        return await ctx.reply("All coordinates must be numeric.")
    try:
        system, dist = await GalaxySystem.get_nearby(
            x_coord=xcoord, y_coord=ycoord, z_coord=zcoord
        )
    except NoResultsEDSM:
        return await ctx.reply(
            f"No system and/or commander named {system} was found in the EDSM database."
        )
    except EDSMLookupError:
        logger.exception("Failed to query EDSM for coordinate details.")
        return await ctx.reply("Failed to query EDSM for coordinate details.")
    if system is None:
        return await ctx.reply(
            f"No systems known to EDSM within 100ly of {xcoord}, {ycoord}, {zcoord}."
        )
    return await ctx.reply(f"{system} is {dist} LY from {xcoord}, {ycoord}, {zcoord}.")


@Commands.command("diversion")
async def cmd_diversionlookup(ctx: Context, args: List[str]):
    """
    Calculate the closest DSSA Carrier to a known EDSM system.

    Usage: !diversion <--new> [system/cmdr]
    Aliases: n/a
    File Last Updated: 2022-05-23 w/ 7,384 Qualified Stations
    """

    cache_override = False

    if len(args) == 0:
        return await ctx.reply(get_help_text("diversion"))
    if args[0] == "--new":
        cache_override = True
        del args[0]

    system = ctx.message.strip()
    cleaned_sys = await sys_cleaner(system)

    try:
        first, second, third, fourth, fifth = await diversions(
            edsm_sys_name=cleaned_sys, cache_override=cache_override
        )
        return await ctx.reply(
            f"Closest Diversion Stations to {cleaned_sys}:\n"
            f"1st: {first[0]}, {float(first[4]):,} LY {first[3]} in {first[2]} ({first[1]} LS from entry)\n"
            f"2nd: {second[0]}, {float(second[4]):,} LY {second[3]} in {second[2]} ({second[1]} LS from entry)\n"
            f"3rd: {third[0]}, {float(third[4]):,} LY {third[3]} in {third[2]} ({third[1]} LS from entry)\n"
            f"4th: {fourth[0]}, {float(fourth[4]):,} LY {fourth[3]} in {fourth[2]} ({fourth[1]} LS from entry)\n"
            f"5th: {fifth[0]}, {float(fifth[4]):,} LY {fifth[3]} in {fifth[2]} ({fifth[1]} LS from entry)"
        )
    except NoResultsEDSM:
        return await ctx.reply(
            f"No system and/or commander named {system} was found in the EDSM database."
        )
    except EDSMLookupError:
        logger.exception("Failed to query EDSM for coordinate details.")
        return await ctx.reply("Failed to query EDSM for coordinate details.")
