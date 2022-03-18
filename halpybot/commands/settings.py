"""
HalpyBOT v1.5.3

settings.py - bot settings commands

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List

import pydle
import logging

from ..packages.checks import Require, Cyberseal, Moderator
from ..packages.configmanager import config_write, config
from ..packages.command import CommandGroup, Commands, get_help_text
from ..packages.models import Context
from ..packages.database import Grafana

logger = logging.getLogger(__name__)
logger.addHandler(Grafana)

Settings = CommandGroup()
Settings.add_group("bot_management", "settings")


@Settings.command("nick")
@Require.permission(Cyberseal)
async def cmd_nick(ctx: Context, args: List[str]):
    """
    Change the nickname of the bot

    Usage: !bot_management nick [newnick]
    Aliases: settings nick
    """
    if len(args) == 0:
        return await ctx.reply(get_help_text("settings nick"))
    logger.info(f"NICK CHANGE from {config['IRC']['nickname']} to {args[0]} by {ctx.sender}")
    await ctx.bot.set_nickname(args[0])
    # Write changes to config file
    config_write('IRC', 'nickname', args[0])


@Settings.command("prefix")
@Require.permission(Cyberseal)
async def cmd_prefix(ctx: Context, args: List[str]):
    """
    Oh boy, I hope you know what you're doing...
    Change the prefix

    Usage: !bot_management prefix [newprefix]
    Aliases: settings prefix
    """
    if not args:
        return await ctx.reply(get_help_text("settings prefix"))
    logger.info(f"PREFIX CHANGE from {config['IRC']['commandPrefix']} by {ctx.sender}")
    config_write('IRC', 'commandPrefix', args[0])
    await ctx.reply(f"Changed prefix to '{args[0]}'")
    await ctx.bot.message(f"#cybers", f"Warning, prefix changed to {args[0]} by "
                                      f"{ctx.sender}!")


@Settings.command("offline")
@Require.permission(Cyberseal)
@Require.channel()
async def cmd_offline(ctx: Context, args: List[str]):
    """
    Change the status of Offline mode.

    Usage: !bot_management offline [Status]
    Aliases: settings offline
    """
    if len(args) == 0:
        return await ctx.reply(f"{get_help_text('settings offline')}\nCurrent "
                               f"offline setting: {config['Offline Mode']['enabled']}")
    if args[0].lower() == "true" and config['Offline Mode']['enabled'] != 'True':
        set_to = "True"
    elif args[0].lower() == "false" and config['Offline Mode']['enabled'] != 'False':
        set_to = "False"
        config_write('Offline Mode', 'warning override', 'False')
    else:
        return await ctx.reply("Error! Invalid parameters given or already in mode. Status not changed.")

    logger.info(f"OFFLINE MODE CHANGE from {config['Offline Mode']['enabled']} to {set_to.upper()} by {ctx.sender}")
    # Write changes to config file
    config_write("Offline Mode", "enabled", "{0}".format(set_to))
    await ctx.reply(f"Warning! Offline Mode Status Changed to {set_to.upper()}")


@Settings.command("warning_override")
@Require.permission(Moderator)
async def cmd_override_omw(ctx: Context, args: List[str]):
    """
    Enable override for offline mode notifications

    Usage: !settings warning_override [Enable/True | Disable/False]
    Aliases: n/a
    """

    if len(args) == 0 or len(args) == 1:
        return await ctx.reply(f"{get_help_text('settings warning_override')}\n"
                               f"Current warning override setting: {config['Offline Mode']['warning override']}")
    request = args[0].lower()

    if request in ('enable', 'true'):
        config_write('Offline Mode', 'warning override', 'True')
        request = True
    elif request in ('disable', 'false'):
        config_write('Offline Mode', 'warning override', 'False')
        request = False
    if request is True or request is False:
        return await ctx.reply(f"Override has been {'enabled.' if request is True else 'disabled.'} You MUST "
                               f"inform an on-duty cyberseal of this action immediately.")


@Commands.command("joinchannel")
@Require.permission(Cyberseal)
async def cmd_joinchannel(ctx: Context, args: List[str]):
    """
    Make the bot join a channel. After restart, it will still be in the channel.
    To make it leave, use !partchannel

    Usage: !joinchannel [channel]
    Aliases: n/a
    """
    if len(args) == 0:
        return await ctx.reply(get_help_text("joinchannel"))
    try:
        await ctx.bot.join(args[0])
        return await ctx.reply(f"Bot joined channel {args[0]}")
    except pydle.client.AlreadyInChannel:
        return await ctx.reply("Bot is already in that channel!")
    except ValueError:
        return await ctx.reply(f"Channel {args[0]} does not exist.")


@Commands.command("partchannel")
@Require.permission(Cyberseal)
async def cmd_part(ctx: Context, args: List[str]):
    """
    Make the bot leave the channel it's currently in

    Usage: !partchannel
    Aliases: n/a
    """
    if len(args) == 0:
        return await ctx.reply(get_help_text("partchannel"))
    try:
        await ctx.bot.part(message=f"Parted by {ctx.sender}", channel=ctx.channel)
        return await ctx.redirect(f"Bot parted channel {args[0]}")
    except pydle.client.NotInChannel:
        return await ctx.reply("Bot is not in that channel!")
    except ValueError:
        return await ctx.reply(f"Channel {args[0]} does not exist.")
