"""
HalpyBOT v1.1

commands\__init__.py - Command initialization script

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List
from src.packages.command.commandhandler import Commands
from datetime import datetime
from .announcer import *
from .bot_management import *
from .delayedboard import *
from .fact import *
from .forcejoin import *
from .edsm import *
from .userinfo import *
from src.packages.database.latency import latency
import time
from src.packages.checks.checks import require_permission, DeniedMessage

@Commands.command("ping")
async def cmd_ping(ctx, args: List[str]):
    """
    https://tinyurl.com/yylju9hg
    Ping the bot, to check if it is alive

    Usage: !ping
    Aliases: n/a
    """
    await ctx.reply("Pong!")


@Commands.command("utc")
async def utc(ctx, args: List[str]):
    """
    Reply with the current UTC/In Game Time

    Usage: !UTC
    Aliases: n/a
    """
    curr_datetime = datetime.utcnow()
    current_utc = curr_datetime.strftime("%H:%M:%S")
    current_monthday = curr_datetime.strftime("%d %B")
    year = datetime.now().year
    year = str(year + 1286)
    await ctx.reply("It is currently " + current_utc + " UTC on " + current_monthday + ", " + year)


@Commands.command("year")
async def year(ctx, args: List[str]):
    """
    Reply with the current In Game Year

    Usage: !year
    Aliases: n/a
    """
    year = datetime.now().year
    year = str(year + 1286)
    await ctx.reply("It is currently the year " + year)

@Commands.command("dbping")
@require_permission(req_level="CYBER", message=DeniedMessage.CYBER)
async def cmd_dbping(ctx, args: List[str]):
    """
    Reply with the latency between the Bot and the Database.

    Usage: !dbping
    Aliases: n/a
    """
    start = time.time()
    latencycheck = await latency()
    final = round(latencycheck - start, 2)
    await ctx.reply("Database Latency: " + str(final) + " seconds")


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
        return await ctx.reply(str(er))  # Return error if one is raised down the call stack.
    finish = time.time()
    final = round(finish - start, 2)
    await ctx.reply("EDSM Latency: " + str(final) + " seconds")
