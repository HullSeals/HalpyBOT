"""
HalpyBOT v1.6

time.py - get in-game time

Copyright (c) 2022 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List
from datetime import datetime

from ..packages.command import Commands
from ..packages.models import Context


@Commands.command("utc")
async def cmd_utc(ctx: Context, args: List[str]):
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
    await ctx.reply(f"It is currently {current_utc} UTC on {current_monthday}, {year}")


@Commands.command("year")
async def cmd_year(ctx: Context, args: List[str]):
    """
    Reply with the current In Game Year

    Usage: !year
    Aliases: n/a
    """
    year = datetime.now().year
    year = str(year + 1286)
    await ctx.reply(f"It is currently the year {year}")
