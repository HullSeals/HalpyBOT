import main
from typing import List
import logging
from .checks import require_dm, require_permission, DeniedMessage
from config import ChannelArray


async def ping(bot: main, channel: str, sender: str, in_channel: bool, args: List[str]):
    logging.info(f"PING {sender} {channel}")
    await bot.reply(channel, sender, in_channel, "Pong!")

@require_dm()
@require_permission(req_level="CYBER", message=DeniedMessage.GENERIC)
async def say(bot: main, channel: str, sender: str, in_channel: bool, args: List[str]):
    logging.info(f"PUPPET SAY {sender} {channel}")
    await bot.message(str(args[0]), ' '.join(args[1:]))


@require_permission(req_level="CYBER", message=DeniedMessage.CYBER)
async def joinchannel(bot: main, channel: str, sender: str, in_channel: bool, args: List[str]):
    # Check if argument starts with a #
    if args[0].startswith("#"):
        await bot.join(args[0])
        ChannelArray.channels.append(args[0])
        return
    if args[0] in ChannelArray.channels:
        return await bot.reply(channel, sender, in_channel, "Bot is already on that channel!")
    else:
        bot.reply(channel, sender, in_channel, "That's not a channel!")


@require_permission(req_level="CYBER", message=DeniedMessage.CYBER)
async def part(bot: main, channel: str, sender: str, in_channel: bool, args: List[str]):
    await bot.part(message=f"PART by {sender}", channel=channel)
    ChannelArray.channels.remove(__value=str(args[0]))


# Just leave this here, it makes it easier to test stuff.
@require_permission(req_level="CYBER", message=DeniedMessage.GENERIC)
async def test_command(bot: main, channel: str, sender: str, in_channel: bool, args: List[str]):
    return
