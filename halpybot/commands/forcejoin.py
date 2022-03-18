"""
HalpyBOT v1.5.2

forcejoin.py - SAJOIN command module

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List

from ..packages.checks import Require, Drilled
from ..packages.command import Commands, get_help_text
from ..packages.models import User
from ..packages.configmanager import config
from ..packages.models import Context


@Commands.command("forcejoin")
@Require.channel()
@Require.permission(Drilled)
async def cmd_sajoin(ctx: Context, args: List[str]):
    """
    Make the bot force a user to join a channel.

    Usage: !forcejoin [user] [channel]
    Aliases: n/a
    """
    if len(args) == 0 or len(args) == 1:
        return await ctx.reply(get_help_text("forcejoin"))

    # Convert channel name to lower case to avoid issues with the already-in-channel check
    args[1] = args[1].lower()

    botuser = await User.get_info(ctx.bot, ctx.bot.nickname)

    # Shockingly, I couldn't find an easier way to do this. If you find one, let me know.
    try:
        channels = await User.get_channels(ctx.bot, args[0])
    except AttributeError:
        return await ctx.reply(f"User {args[0]} doesn't appear to exist...")

    if args[1] not in config["Force join command"]["joinable"].lower():
        return await ctx.reply("I can't move people there.")

    if args[1] in channels:
        return await ctx.reply("User is already on that channel!")

    # Check if bot is oper. Let's do this properly later
    if not botuser.oper:
        return await ctx.reply(
            "Cannot comply: I'm not an IRC operator! Contact a cyberseal"
        )

    # Then, let user join the channel
    await ctx.bot.rawmsg("SAJOIN", args[0], args[1])

    # Now we manually confirm that the SAJOIN was successful
    channels = await User.get_channels(ctx.bot, args[0])

    if args[1].lower() in channels:
        return await ctx.reply(f"{str(args[0])} forced to join {str(args[1])}")
    return await ctx.reply("Oh noes! something went wrong, contact a cyberseal!")


@Commands.command("rrjoin")
@Require.channel()
@Require.permission(Drilled)
async def cmd_rrjoin(ctx: Context, args: List[str]):
    """
    Make the bot force a user to join the repair channel.

    Usage: !rrjoin [user]
    Aliases: n/a
    """
    if len(args) == 0:
        return await ctx.reply(get_help_text("rrjoin"))

    botuser = await User.get_info(ctx.bot, ctx.bot.nickname)

    # Shockingly, I couldn't find an easier way to do this. If you find one, let me know.
    try:
        channels = await User.get_channels(ctx.bot, args[0])
    except AttributeError:
        return await ctx.reply(f"User {args[0]} doesn't appear to exist...")

    if "#repair-requests" in channels:
        return await ctx.reply("User is already on that channel!")

    # Check if bot is oper. Let's do this properly later
    if not botuser.oper:
        return await ctx.reply(
            "Cannot comply: I'm not an IRC operator! Contact a cyberseal"
        )

    # Then, let user join the channel
    await ctx.bot.rawmsg("SAJOIN", args[0], "#repair-requests")

    # Now we manually confirm that the SAJOIN was successful
    channels = await User.get_channels(ctx.bot, args[0])

    if "#repair-requests" in channels:
        return await ctx.reply(f"{str(args[0])} forced to join #Repair-Requests")
    else:
        return await ctx.reply(f"Oh noes! something went wrong, contact a cyberseal!")
