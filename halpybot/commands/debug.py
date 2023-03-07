"""
debug.py - Debug Test Commands for 2.0

MUST BE REMOVED BEFORE LIVE

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
from typing import List
from ..packages.command import Commands
from ..packages.models import Context, Platform


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


@Commands.command("fullboard")
async def cmd_fullboard(ctx: Context, args: List[str]):
    await ctx.bot.board.debug_full_board
    return await ctx.reply("Debug Full Data Loaded!")


@Commands.command("newcase")
async def cmd_newcase(ctx: Context, args: List[str]):
    cmdr = args[0]
    plt = Platform(int(args[1])).name
    sys = args[2]
    case = await ctx.bot.board.add_case(client=cmdr, platform=plt, system=sys)
    return await ctx.reply(f"New case started: Board ID {case.board_id}")
