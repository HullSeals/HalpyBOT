import main
from typing import List


async def ping(bot: main, channel: str, sender: str, args: List[str], in_channel: bool):
    if in_channel:
        bot.message(channel, "Pong!")
    else:
        bot.message(sender, "Pong!")