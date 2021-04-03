"""
HalpyBOT v1.4

settings.py - bot settings commands

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List

import pydle
import logging

from ...packages.checks import *
from ...packages.configmanager import config_write, config
from ...packages.command import CommandGroup, Commands

Settings = CommandGroup()
Settings.add_group("bot_management", "settings")

@Settings.command("nick")
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
    config_write('IRC', 'nickname', args[0])


@Settings.command("prefix")
@require_permission(req_level="CYBER", message=DeniedMessage.CYBER)
async def cmd_prefix(ctx, args: List[str]):
    """
    Oh boy, I hope you know what you're doing...
    Change the prefix

    Usage: !bot_management prefix [newprefix]
    Aliases: settings prefix
    """
    logging.info(f"PREFIX CHANGE from {config['IRC']['commandPrefix']} by {ctx.sender}")
    config_write('IRC', 'commandPrefix', args[0])
    await ctx.reply(f"Changed prefix to '{args[0]}'")
    await ctx.bot.message(f"#cybers", f"Warning, prefix changed to {args[0]} by "
                                      f"{ctx.sender}! Rik079!")

@Settings.command("offline")
@require_permission(req_level="CYBER", message=DeniedMessage.CYBER)
@require_channel()
async def cmd_offline(ctx, args: List[str]):
    """
    Change the status of Offline mode.

    Usage: !bot_management offline [Status]
    Aliases: settings offline
    """
    if not len(args) == 1:
        if len(args) == 0:
            return await ctx.reply(f"Current offline setting: {config['Offline Mode']['enabled']}")
        return await ctx.reply("Usage: !bot_management offline [Status]")

    if args[0].lower() == "true" and config['Offline Mode']['enabled'] != 'True':
        set_to = "True"
    elif args[0].lower() == "false" and config['Offline Mode']['enabled'] != 'False':
        set_to = "False"
        config_write('Offline Mode', 'warning override', 'False')
    else:
        return await ctx.reply("Error! Invalid parameters given or already in mode. Status not changed.")

    logging.info(f"OFFLINE MODE CHANGE from {config['Offline Mode']['enabled']} to {set_to.upper()} by {ctx.sender}")
    # Write changes to config file
    config_write("Offline Mode", "enabled", "{0}".format(set_to))
    await ctx.reply(f"Warning! Offline Mode Status Changed to {set_to.upper()}")


@Settings.command("warning_override")
@require_permission(req_level="MODERATOR", message=DeniedMessage.MODERATOR)
async def cmd_override_omw(ctx, args: List[str]):
    """
    Enable override for offline mode notifications

    Usage: !settings warning_override [Enable/True | Disable/False]
    Aliases: n/a
    """

    if len(args) not in (0, 1):
        return await ctx.reply("Cannot comply: invalid parameters given.")
    if len(args) == 0:
        return await ctx.reply(f"Warning Override setting: {config['Offline Mode']['warning override']}")

    request = args[0].lower()

    if request in ('enable', 'true'):
        config_write('Offline Mode', 'warning override', 'True')
        request = True
    elif request in ('disable', 'false'):
        config_write('Offline Mode', 'warning override', 'False')
        request = False
    else:
        return await ctx.reply("Usage: !settings warning_override [enable | disable]")

    return await ctx.reply(f"Override has been {'enabled.' if request is True else 'disabled.'} You MUST "
                           f"inform an on-duty cyberseal of this action immediately.")


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
