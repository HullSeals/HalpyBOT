import main
from typing import List
import logging


async def ping(bot: main, channel: str, sender: str, args: List[str], in_channel: bool):
    logging.info(f"PING {sender} {channel}")
    await bot.reply(channel, sender, in_channel, "Pong!")

