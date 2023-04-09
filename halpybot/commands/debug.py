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
from ..packages.models import Context, Case


@Commands.command("nextid")
async def cmd_nextid(ctx: Context, args: List[str]):
    await ctx.reply(f"ID: {ctx.bot.board.open_rescue_id}")


@Commands.command("delcase")
async def cmd_clearboard(ctx: Context, args: List[str]):
    try:
        caseref = int(args[0])
    except ValueError:
        caseref = args[0]
    try:
        case: Case = ctx.bot.board.return_rescue(caseref)
    except KeyError:
        return await ctx.reply("[DEBUG] No case found.")
    await ctx.bot.board.del_case(case)
    return await ctx.reply("Case Cleared!")


@Commands.command("debugwelcome")
async def cmd_debugwelcome(ctx: Context, args: List[str]):
    try:
        caseref = int(args[0])
    except ValueError:
        caseref = args[0]
    try:
        case: Case = ctx.bot.board.return_rescue(caseref)
    except KeyError:
        return await ctx.reply("[DEBUG] No case found.")
    mod_kwargs = {"welcomed": True}
    await ctx.bot.board.mod_case(case.board_id, **mod_kwargs)
    return await ctx.reply(f"[DEBUG] case {caseref} set to Welcomed.")
