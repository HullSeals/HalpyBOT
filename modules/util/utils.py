from typing import List
import logging
from .checks import require_dm, require_permission, DeniedMessage
from main import channels

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
    Make the bot join a channel. it won't rejoin after the bot disconnects.
    If the bot should always join this channel, put it in the config file

    Usage: !joinchannel [channel]
    Aliases: n/a
    """
    # Check if argument starts with a #
    if args[0].startswith("#"):
        await ctx.bot.join(args[0])
        # TODO add to config-channels
        return
    if args[0] in channels:
        return await ctx.reply("Bot is already on that channel!")
    else:
        ctx.reply("That's not a channel!")


@require_permission(req_level="CYBER", message=DeniedMessage.CYBER)
async def cmd_part(ctx, args: List[str]):
    """
    Make the bot leave the channel it's currently in

    Usage: !partchannel
    Aliases: n/a
    """
    await ctx.bot.part(message=f"PART by {ctx.sender}", channel=ctx.channel)
    # TODO remove from config-channels


# Just leave this here, it makes it easier to test stuff.
@require_permission(req_level="CYBER", message=DeniedMessage.GENERIC)
async def cmd_test(ctx, args: List[str]):
    return
