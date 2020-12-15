"""
HalpyBOT v1.1

utils.py - miscellaneous management commands

Copyright (c) 2020 The Hull Seals,
All rights reserved

Licensed under the GNU General Public License
See license.md
"""


from typing import List
import logging
from .checks import require_channel, require_dm, require_permission, DeniedMessage
from main import config
import pydle

joinableChannels = [entry.strip() for entry in config.get('Force join command', 'joinable').split(',')]

async def cmd_ping(ctx, args: List[str]):
    """
    https://tinyurl.com/yylju9hg
    Ping the bot, to check if it is alive

    Usage: !ping
    Aliases: n/a
    """
    await ctx.reply("Pong!")

@require_dm()
@require_permission(req_level="CYBER", message=DeniedMessage.GENERIC)
async def cmd_say(ctx, args: List[str]):
    """
    Make the bot say something

    Usage: !say [channel] [text]
    Aliases: n/a
    """
    await ctx.bot.message(str(args[0]), ' '.join(args[1:]))


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
        except pydle.client.AlreadyInChannel as er:
            await ctx.reply("Bot is already in that channel!")
    else:
        await ctx.reply("That's not a channel!")


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


# Just leave this here, it makes it easier to test stuff.
@require_permission(req_level="CYBER", message=DeniedMessage.GENERIC)
async def cmd_test(ctx, args: List[str]):
    return


@require_channel()
@require_permission(req_level="DRILLED", message=DeniedMessage.DRILLED)
async def cmd_sajoin(ctx, args: List[str]):
    """
    Make the bot force a user to join a channel.

    Usage: !forcejoin [user] [channel]
    Aliases: n/a
    """
    botuser = await ctx.bot.whois(config['IRC']['nickname'])  # FIXME ew, un-stupidify this ASAP

    try:
        user = await ctx.bot.whois(nickname=args[0])
    except AttributeError:  # This is retarded. I know.
        logging.error(f"Unable to WHOIS on !forcejoin user: {args[0]}. See {ctx.channel}")
        return await ctx.reply("That user doesn't seem to exist!")

    channels = [ch.translate({ord(c): None for c in '+%@&~'}) for ch in user['channels']]

    if args[1] not in joinableChannels:
        return await ctx.reply("I can't move people there.")

    if str(args[1]) in channels:
        return await ctx.reply("User is already on that channel!")

    # Check if bot is oper. Let's do this properly later
    if not botuser['oper']:
        return await ctx.reply("Cannot comply: I'm not an IRC operator! Contact a cyberseal")

    # Then, let user join the channel
    await ctx.bot.rawmsg('SAJOIN', args[0], args[1])
    await ctx.reply(f"{str(args[0])} forced to join {str(args[1])}")

    # Now we manually confirm that the SAJOIN was successful
    if str(args[1]) in channels:
        return await ctx.reply(f"{args[0]} is now in {args[1]}.")
    else:
        return await ctx.reply(f"Oh noes! something went wrong, contact a cyberseal!")
