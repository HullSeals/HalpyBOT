"""
ping.py - Ping the bot, database, and external services

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import time
from typing import List
from loguru import logger
import aiohttp
from ..packages.command import Commands
from ..packages.checks import Require, Cyberseal
from ..packages.database import latency, NoDatabaseConnection
from ..packages.edsm import GalaxySystem, EDSMLookupError, EDSMConnectionError
from ..packages.models import Context
from ..packages.utils import web_get


@Commands.command("ping")
async def cmd_ping(ctx: Context, args: List[str]):
    """
    https://tinyurl.com/yylju9hg
    Ping the bot, to check if it is alive

    Usage: !ping
    Aliases: n/a
    """
    await ctx.reply("Pong!")


@Commands.command("dbping")
@Require.permission(Cyberseal)
async def cmd_dbping(ctx: Context, args: List[str]):
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
        await ctx.reply(f"Database Latency: {str(final)} seconds")
    else:
        await ctx.reply(latencycheck)


@Commands.command("edsmping")
@Require.permission(Cyberseal)
async def cmd_edsmping(ctx: Context, args: List[str]):
    """
    Reply with the latency between the Bot and the EDSM API.

    Usage: !edsmping
    Aliases: n/a
    """
    start = time.time()
    try:
        await GalaxySystem.exists(name="Sol", cache_override=True)
    except EDSMLookupError:
        logger.exception("Failed to query EDSM.")
        return await ctx.reply("Failed to query EDSM.")
    finish = time.time()
    final = round(finish - start, 2)
    await ctx.reply(f"EDSM Latency: {str(final)} seconds")


@Commands.command("serverstatus")
async def cmd_serverstat(ctx: Context, args: List[str]):
    """
    Reply with the current Elite server status according to EDSM.

    Usage: !serverstatus
    Aliases: n/a
    """
    try:
        uri = "https://hosting.zaonce.net/launcher-status/status.json"
        responses = await web_get(uri)
    except aiohttp.ClientError as e:
        logger.exception("Error in Elite Server Status lookup.")
        raise EDSMConnectionError(
            "Unable to verify Elite Status, having issues connecting to the Elite API."
        ) from e
    if len(responses) == 0:
        return await ctx.reply("ERROR! Elite returned an empty reply.")
    message = responses["text"]
    code = responses["status"]
    await ctx.reply(
        f"The Elite servers are {message} (Status Code {code}) according to Frontier."
    )
