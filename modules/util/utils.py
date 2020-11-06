import main
from typing import List
import logging
from .checks import require_dm, require_permission, DeniedMessage


async def ping(bot: main, channel: str, sender: str, args: List[str], in_channel: bool):
    logging.info(f"PING {sender} {channel}")
    await bot.reply(channel, sender, in_channel, "Pong!")

@require_dm()
@require_permission(req_level="CYBER", message=DeniedMessage.GENERIC)
async def say(bot: main, channel: str, sender: str, args: List[str], in_channel: bool):
    logging.info(f"PUPPET SAY {sender} {channel}")
    await bot.message(str(args[0]), ' '.join(args[1:]))

# Just leave this here, it makes it easier to test stuff.
@require_permission(req_level="CYBER", message=DeniedMessage.GENERIC)
async def test_command(bot: main, channel: str, sender: str, args: List[str], in_channel: bool):
    return
