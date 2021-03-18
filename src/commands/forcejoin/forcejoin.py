"""
HalpyBOT v1.2.2

forcejoin.py - SAJOIN command module

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List

from main import config
from src.packages.checks.checks import require_channel, require_permission, DeniedMessage
from .. import Commands
from src.packages.datamodels.user import User

joinableChannels = [entry.strip() for entry in config.get('Force join command', 'joinable').split(',')]


@Commands.command("forcejoin")
@require_channel()
@require_permission(req_level="DRILLED", message=DeniedMessage.DRILLED)
async def cmd_sajoin(ctx, args: List[str]):
    """
    Make the bot force a user to join a channel.

    Usage: !forcejoin [user] [channel]
    Aliases: n/a
    """
    # Convert channel name to lower case to avoid issues with the already-in-channel check
    args[1] = args[1].lower()

    botuser = await User.get_info(ctx, ctx.bot.nickname)

    channels = await User.get_channels(ctx, args[0])

    if args[1] not in joinableChannels:
        return await ctx.reply("I can't move people there.")

    if args[1] in channels:
        return await ctx.reply("User is already on that channel!")

    # Check if bot is oper. Let's do this properly later
    if not botuser.oper:
        return await ctx.reply("Cannot comply: I'm not an IRC operator! Contact a cyberseal")

    # Then, let user join the channel
    await ctx.bot.rawmsg('SAJOIN', args[0], args[1])

    # Now we manually confirm that the SAJOIN was successful
    channels = await User.get_channels(ctx, args[0])

    if args[1] in channels:
        return await ctx.reply(f"{str(args[0])} forced to join {str(args[1])}")
    else:
        return await ctx.reply(f"Oh noes! something went wrong, contact a cyberseal!")
