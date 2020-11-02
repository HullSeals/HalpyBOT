import main
from typing import List


async def ping(bot: main, channel: str, sender: str, args: List[str], in_channel: bool):
    await bot.reply(channel, sender, in_channel, "Pong!")
