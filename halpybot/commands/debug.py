"""
debug.py - Debug Test Commands for 2.0

MUST BE REMOVED BEFORE LIVE

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
from typing import List
from ..packages.command import Commands, get_help_text
from ..packages.models import Context


@Commands.command("nextid")
async def cmd_nextid(ctx: Context, args: List[str]):
    await ctx.reply(f"ID: {ctx.bot.board.open_rescue_id}")


@Commands.command("loadboard")
async def cmd_loadboard(ctx: Context, args: List[str]):
    await ctx.bot.board.debug_load_board
    return await ctx.reply("Debug Data Loaded!")


@Commands.command("clearboard")
async def cmd_clearboard(ctx: Context, args: List[str]):
    await ctx.bot.board.debug_clear_board
    return await ctx.reply("Board Cleared!")
