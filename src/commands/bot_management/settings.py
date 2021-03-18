"""
HalpyBOT v1.2.2

settings.py - bot settings commands

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List

import pydle

from src.packages.checks.checks import require_permission, DeniedMessage
from main import config
import logging
from src.packages.configmanager.edit import config_write
from .. import Commands


@require_permission(req_level="CYBER", message=DeniedMessage.CYBER)
async def cmd_nick(ctx, args: List[str]):
    """
    Change the nickname of the bot

    Usage: !bot_management nick [newnick]
    Aliases: settings nick
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

    Usage: !bot_management prefix [newprefix]
    Aliases: settings prefix
    """
    logging.info(f"PREFIX CHANGE from {config['IRC']['commandPrefix']} by {ctx.sender}")
    await config_write('IRC', 'commandPrefix', args[0])
    await ctx.reply(f"Changed prefix to '{args[0]}'")
    await ctx.bot.message(f"#cybers", f"Warning, prefix changed to {args[0]} by "
                                      f"{ctx.sender}! Rik079!")


# Create the command group

@Commands.command("settings", "bot_management")
async def cmd_group_settings(ctx, args: List[str]):
    subcommands = {
        'nick': cmd_nick,
        'prefix': cmd_prefix,
    }
    if len(args) == 0:
        await ctx.reply(f"Available bot_management: {', '.join(scmd for scmd in subcommands.keys())}")
    elif args[0] in subcommands.keys():
        subcommand = args[0]
        args = args[1:]
        await subcommands[subcommand](ctx, args)
    else:
        await ctx.reply("Subcommand not found! Try !bot_management to see all the options")


@Commands.command("joinchannel")
@require_permission(req_level="CYBER", message=DeniedMessage.CYBER)
async def cmd_joinchannel(ctx, args: List[str]):
    """
    Make the bot join a channel. After restart, it will still be in the channel.
    To make it leave, use !partchannel

    Usage: !joinchannel [channel]
    Aliases: n/a
    """
    # Check if argument starts with a #
    if args[0].startswith("#"):
        try:
            await ctx.bot.join(args[0])
            await ctx.reply(f"Bot joined channel {str(args[0])}")
            config['Channels']['ChannelList'] += f", {args[0]}"
            with open('config/config.ini', 'w') as conf:
                config.write(conf)
            await ctx.reply("Config file updated.")
            return
        except pydle.client.AlreadyInChannel:
            await ctx.reply("Bot is already in that channel!")
    else:
        await ctx.reply("That's not a channel!")


@Commands.command("partchannel")
@require_permission(req_level="CYBER", message=DeniedMessage.CYBER)
async def cmd_part(ctx, args: List[str]):
    """
    Make the bot leave the channel it's currently in

    Usage: !partchannel
    Aliases: n/a
    """
    channels = [entry.strip() for entry in config.get('Channels', 'ChannelList').split(',')]
    await ctx.bot.part(message=f"PART by {ctx.sender}", channel=ctx.channel)
    channels.remove(str(ctx.channel))
    config['Channels']['ChannelList'] = ', '.join(ch for ch in channels)
    with open('config/config.ini', 'w') as conf:
        config.write(conf)
