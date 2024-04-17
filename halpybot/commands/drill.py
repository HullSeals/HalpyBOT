"""
drill.py - Commands for the training and drilling of Seals

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List
from ..packages.command import Commands, get_help_text
from ..packages.checks import Drilled, needs_permission, in_channel
from ..packages.models import Context
from ..packages.announcer.announcer import get_edsm_data
from ..packages.utils import sys_cleaner


@Commands.command("drillcase")
@needs_permission(Drilled)
@in_channel
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
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, "drillcase"))
    system = await sys_cleaner(args[2])
    await ctx.reply(
        f"xxxx DRILL -- DRILL -- DRILL xxxx\n"
        f"CMDR: {args[0]} -- Platform: {args[1]}\n"
        f"System: {system} -- Hull: {args[3]}\n"
        f"xxxxxxxx"
    )
    await ctx.reply(await lookup(system))


@Commands.command("drillkfcase")
@needs_permission(Drilled)
@in_channel
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
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, "drillkfcase"))
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
@needs_permission(Drilled)
@in_channel
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
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, "drillcbcase"))
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
    args = {"System": system}
    return await get_edsm_data(args)
