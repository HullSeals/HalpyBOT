"""
HalpyBOT v1.6

drill.py - Commands for the training and drilling of Seals

Copyright (c) 2022 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
from typing import List

import halpybot.packages.announcer.announcer
from ..packages.command import Commands, get_help_text
from ..packages.checks import Require, Drilled
from ..packages.models import Context
from ..packages.edsm import (
    checklandmarks,
    EDSMLookupError,
    checkdssa,
    sys_cleaner,
    NoResultsEDSM,
    get_nearby_system,
)


CACHE_OVERRIDE = False


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
    # Clean out the list, only pass "full" args.
    args = [x.strip(" ") for x in args]
    args = [ele for ele in args if ele.strip()]
    if len(args) < 4:
        return await ctx.reply(get_help_text("drillcase"))
    system = await sys_cleaner(args[2])
    await ctx.reply(
        f"xxxx DRILL -- DRILL -- DRILL xxxx\n"
        f"CMDR: {args[0]} -- Platform: {args[1]}\n"
        f"System: {system} -- Hull: {args[3]}\n"
        f"xxxxxxxx"
    )
    await ctx.reply(await lookup(system))


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
    # Clean out the list, only pass "full" args.
    args = [x.strip(" ") for x in args]
    args = [ele for ele in args if ele.strip()]
    if len(args) < 6:
        return await ctx.reply(get_help_text("drillkfcase"))
    system = await sys_cleaner(args[2])
    await ctx.reply(
        f"xxxx DRILL -- DRILL -- DRILL xxxx\n"
        f"CMDR: {args[0]} -- Platform: {args[1]}\n"
        f"System: {system} -- Planet: {args[3]}\n"
        f"Coordinates: {args[4]}\n:"
        f"Type: {args[5]}\n"
        f"xxxxxxxx"
    )
    await ctx.reply(await lookup(system))


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
    # Clean out the list, only pass "full" args.
    args = [x.strip(" ") for x in args]
    args = [ele for ele in args if ele.strip()]
    if len(args) < 6:
        return await ctx.reply(get_help_text("drillcbcase"))
    system = await sys_cleaner(args[2])
    await ctx.reply(
        f"xxxx DRILL -- DRILL -- DRILL xxxx\n"
        f"CMDR: {args[0]} -- Platform: {args[1]}\n"
        f"System: {system} -- Hull: {args[3]}\n"
        f"Can Synth: {args[4]} -- O2 Timer: {args[5]}\n"
        f"xxxxxxxx"
    )
    await ctx.reply(await lookup(system))


async def lookup(system):
    """Calculates and formats a ready-to-go string with EDSM info about a system

    Args:
        system (str): The system being called by the Trainer

    Returns:
        (str) string with information about the existence of a system, plus
            distance and cardinal direction from the nearest landmark
    """
    sys_name = system
    try:
        exact_sys = sys_name == system
        landmark, distance, direction = await checklandmarks(sys_name)
        # What we have is good, however, to make things look nice we need to flip the direction Drebin Style
        direction = halpybot.packages.announcer.announcer.cardinal_flip[direction]
        if exact_sys:
            return f"System exists in EDSM, {distance} LY {direction} of {landmark}."
        return (
            f"{system} could not be found in EDSM. System closest in name found in EDSM was"
            f" {sys_name}\n{sys_name} is {distance} LY {direction} of {landmark}. "
        )
    except NoResultsEDSM:
        if (
            str(NoResultsEDSM)
            == f"No major landmark systems within 10,000 ly of {system}."
        ):
            dssa, distance, direction = await checkdssa(system)
            return (
                f"{NoResultsEDSM}\nThe closest DSSA Carrier is in {dssa}, {distance} LY {direction} of "
                f"{system}."
            )
        found_sys, close_sys = await get_nearby_system(sys_name)
        if found_sys:
            try:
                landmark, distance, direction = await checklandmarks(close_sys)
                return (
                    f"{system} could not be found in EDSM. System closest in name found in EDSM was"
                    f" {close_sys}\n{close_sys} is {distance} LY {direction} of {landmark}. "
                )
            except NoResultsEDSM:
                if (
                    str(NoResultsEDSM)
                    == f"No major landmark systems within 10,000 ly of {close_sys}."
                ):
                    dssa, distance, direction = await checkdssa(close_sys)
                    return (
                        f"{sys_name} could not be found in EDSM. System closest in name found in "
                        f"EDSM was {close_sys}.\n{NoResultsEDSM}\nThe closest DSSA Carrier is in "
                        f"{dssa}, {distance} LY {direction} of {close_sys}. "
                    )
        return (
            "System Not Found in EDSM. match to sys name format or sys name lookup failed.\nPlease "
            "check system name with client "
        )
    except EDSMLookupError:
        return "Unable to query EDSM"
