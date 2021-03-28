"""
HalpyBOT v1.3

ping.py - Ping the bot, database, and external services

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import time

from .. import Commands
from ...packages.checks import *
from ...packages.database import latency, NoDatabaseConnection
from ...packages.edsm import GalaxySystem, EDSMLookupError

@Commands.command("ping")
async def cmd_ping(ctx, args: List[str]):
    """
    https://tinyurl.com/yylju9hg
    Ping the bot, to check if it is alive

    Usage: !ping
    Aliases: n/a
    """
    await ctx.reply("Pong!")

@Commands.command("dbping")
@require_permission(req_level="CYBER", message=DeniedMessage.CYBER)
async def cmd_dbping(ctx, args: List[str]):
    """
    Reply with the latency between the Bot and the Database.

    Usage: !dbping
    Aliases: n/a
    """
    start = time.time()
    try:
        latencycheck = await latency()
    except NoDatabaseConnection:
        return await ctx.reply("Unable: No connection.")
    if isinstance(latencycheck, float):
        final = round(latencycheck - start, 2)
        await ctx.reply("Database Latency: " + str(final) + " seconds")
    else:
        await ctx.reply(latencycheck)

@Commands.command("edsmping")
@require_permission(req_level="CYBER", message=DeniedMessage.CYBER)
async def cmd_edsmping(ctx, args: List[str]):
    """
    Reply with the latency between the Bot and the EDSM API.

    Usage: !edsmping
    Aliases: n/a
    """
    start = time.time()
    try:
        await GalaxySystem.exists(name="Sol")
    except EDSMLookupError as er:
        return await ctx.reply(str(er))
    finish = time.time()
    final = round(finish - start, 2)
    await ctx.reply("EDSM Latency: " + str(final) + " seconds")
