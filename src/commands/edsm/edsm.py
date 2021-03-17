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
from src.packages.checks.checks import require_channel, require_permission, DeniedMessage
from .. import Commands


@Commands.command("lookup", "syslookup")
async def cmd_systemlookup(ctx, args: List[str]):
    """
    Check EDSM for the existence of a system.

    Usage: !lookup
    Aliases: syslookup
    """

    system = ' '.join(args[0:])
    if not system:
        return await ctx.reply("No system given! Please provide a system name.")
    else:
        try:
            return await ctx.reply(await checksystem(system))
        except Exception as e:
            return await ctx.reply(e)


@Commands.command("locatecmdr", "cmdrlookup", "locate")
async def cmd_cmdrlookup(ctx, args: List[str]):
    """
    Check EDSM for the existence of a CMDR.

    Usage: !locatecmdr
    Aliases: cmdrlookup, locate
    """

    cmdr = ' '.join(args[0:])
    if not cmdr:
        return await ctx.reply("No arguments given! Please provide a CMDR name.")
    else:
        try:
            return await ctx.reply(await locatecmdr(cmdr))
        except Exception as e:
            return await ctx.reply(e)


@Commands.command("distance", "dist")
async def cmd_distlookup(ctx, args: List[str]):
    """
    Check EDSM for the distance between two known points.

    Usage: !distance
    Aliases: dist
    """

    if not args:
        return await ctx.reply("Please provide two points to look up, separated by a :")
    listToStr = ' '.join([str(elem) for elem in args])
    points = listToStr.split(":", 1)
    pointa = ''.join(points[0])
    pointa = pointa.strip()
    pointb = ''.join(points[1])
    pointb = pointb.strip()
    try:
        return await ctx.reply(await checkdistance(pointa, pointb))
    except Exception as e:
        return await ctx.reply(e)
