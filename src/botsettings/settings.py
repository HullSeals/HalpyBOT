"""
HalpyBOT v1.1

settings.py - bot settings modification module

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List
from ..util.checks import require_permission, DeniedMessage
from main import config
import logging
from ..configmanager.edit import config_write


@require_permission(req_level="CYBER", message=DeniedMessage.CYBER)
async def cmd_nick(ctx, args: List[str]):
    """
    Change the nickname of the bot

    Usage: !settings nick [newnick]
    Aliases: n/a
    """
    logging.info(f"NICK CHANGE from {config['IRC']['nickname']} to {args[0]} by {ctx.sender}")
    await ctx.bot.set_nickname(args[0])
    # Write changes to config file
    await config_write('IRC', 'nickname', args[0])


@require_permission(req_level="CYBER", message=DeniedMessage.CYBER)
async def cmd_prefix(ctx, args: List[str]):
    """
    Oh boy, I hope you know what you're doing...
    Change the prefix

    Usage: !settings prefix [newprefix]
    Aliases: n/a
    """
    logging.info(f"PREFIX CHANGE from {config['IRC']['commandPrefix']} by {ctx.sender}")
    await config_write('IRC', 'commandPrefix', args[0])
    await ctx.reply(f"Changed prefix to '{args[0]}'")
    await ctx.bot.message(f"#cybers", f"Warning, prefix changed to {args[0]} by "
                                      f"{ctx.sender}! Rik079!")


# Create the command group
async def cmd_group_settings(ctx, args: List[str]):
    subcommands = {
        'nick': cmd_nick,
        'prefix': cmd_prefix,
    }
    if len(args) == 0:
        await ctx.reply(f"Available settings: {', '.join(scmd for scmd in subcommands.keys())}")
    elif args[0] in subcommands.keys():
        subcommand = args[0]
        args = args[1:]
        await subcommands[subcommand](ctx, args)
    else:
        await ctx.reply("Subcommand not found! Try !settings to see all the options")