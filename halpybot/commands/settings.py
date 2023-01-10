"""
settings.py - bot settings commands

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List
from loguru import logger
import pydle
from ..packages.checks import Require, Cyberseal

from ..packages.command import CommandGroup, Commands, get_help_text
from ..packages.models import Context
from halpybot import config

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
    logger.info(
        "NICK CHANGE from {name} to {newName} by {sender}",
        name=config.irc.nickname,
        newName=args[0],
        sender=ctx.sender,
    )
    await ctx.bot.set_nickname(args[0])


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
    logger.info(
        "PREFIX CHANGE from {prefix} to {new} by {sender}",
        prefix=config.irc.command_prefix,
        new=args[0],
        sender=ctx.sender,
    )
    config.irc.command_prefix = args[0]
    await ctx.reply(f"Changed prefix to '{args[0]}'")
    await ctx.bot.message(
        "#cybers", f"Warning, prefix changed to {args[0]} by {ctx.sender}!"
    )


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
        return await ctx.reply(
            f"{get_help_text('settings offline')}\nCurrent "
            f"offline setting: {config.offline_mode.enabled}"
        )
    if not args[0].casefold() in ("true", "false"):
        return await ctx.reply(
            "Error! Invalid parameters given. Status not changed."
        )
    
    to_offline = args[0].casefold() == "true"

    logger.info(
        "OFFLINE MODE CHANGE from {mode} to {new} by {sender}",
        mode=config.offline_mode.enabled,
        new=to_offline,
        sender=ctx.sender,
    )
    config.offline_mode.enabled = to_offline
    # Write changes to config file
    await ctx.reply(f"Warning! Offline Mode Status Changed to {to_offline}")


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
        await ctx.bot.part(message=f"Parted by {ctx.sender}", channel=args[0])
        return await ctx.redirect(f"Bot parted channel {args[0]}")
    except pydle.client.NotInChannel:
        return await ctx.reply("Bot is not in that channel!")
    except ValueError:
        return await ctx.reply(f"Channel {args[0]} does not exist.")
