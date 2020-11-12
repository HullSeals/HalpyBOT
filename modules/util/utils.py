from typing import List
import logging
from .checks import require_dm, require_permission, DeniedMessage
from main import config
import pydle


async def cmd_ping(ctx, args: List[str]):
    """
    https://tinyurl.com/yylju9hg
    Ping the bot, to check if it is alive

    Usage: !ping
    Aliases: n/a
    """
    logging.info(f"PING {ctx.sender} {ctx.channel}")
    await ctx.reply("Pong!")

@require_dm()
@require_permission(req_level="CYBER", message=DeniedMessage.GENERIC)
async def cmd_say(ctx, args: List[str]):
    """
    Make the bot say something

    Usage: !say [channel] [text]
    Aliases: n/a
    """
    logging.info(f"PUPPET SAY {ctx.sender} {ctx.channel}")
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
