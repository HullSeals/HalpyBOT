"""
misc.py - Miscellaneous Bot Functionality

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
from typing import List
from loguru import logger
from ..packages.utils import shorten
from ..packages.checks import Require, Drilled
from ..packages.command import Commands, get_help_text
from ..packages.models import Context


@Commands.command("shorten")
@Require.permission(Drilled)
async def cmd_shorten(ctx: Context, args: List[str]):
    """
    Shorten a given URL with the configured YOURLS API

    Usage: !shorten --forceHTTP [url]
    Aliases: n/a
    """
    force_http = False
    if len(args) == 0:
        return await ctx.reply(get_help_text("shorten"))
    if args[0] == "--forceHTTP":
        force_http = True
        del args[0]
        if not args:
            return await ctx.reply(get_help_text("lookup"))
    logger.info(f"{ctx.sender} requested shortening of {args[0]}")
    if force_http:
        surl = await shorten(args[0], force_http=True)
    else:
        surl = await shorten(args[0])
    return await ctx.reply(f"{ctx.sender}: Here's your short URL: {surl}.")

