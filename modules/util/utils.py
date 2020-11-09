from typing import List
import logging
from .checks import require_dm, require_permission, DeniedMessage
from config import ChannelArray


async def ping(ctx, args: List[str]):
    logging.info(f"PING {ctx.sender} {ctx.channel}")
    await ctx.reply("Pong!")

@require_dm()
@require_permission(req_level="CYBER", message=DeniedMessage.GENERIC)
async def say(ctx, args: List[str]):
    logging.info(f"PUPPET SAY {ctx.sender} {ctx.channel}")
    await ctx.bot.message(str(args[0]), ' '.join(args[1:]))


@require_permission(req_level="CYBER", message=DeniedMessage.CYBER)
async def joinchannel(ctx, args: List[str]):
    # Check if argument starts with a #
    if args[0].startswith("#"):
        await ctx.bot.join(args[0])
        ChannelArray.channels.append(args[0])
        return
    if args[0] in ChannelArray.channels:
        return await ctx.reply("Bot is already on that channel!")
    else:
        ctx.reply("That's not a channel!")


@require_permission(req_level="CYBER", message=DeniedMessage.CYBER)
async def part(ctx, args: List[str]):
    await ctx.bot.part(message=f"PART by {ctx.sender}", channel=ctx.channel)
    ChannelArray.channels.remove(__value=str(args[0]))


# Just leave this here, it makes it easier to test stuff.
@require_permission(req_level="CYBER", message=DeniedMessage.GENERIC)
async def test_command(ctx, args: List[str]):
    return
