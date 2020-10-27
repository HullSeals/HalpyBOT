import main
from typing import List

from .fact_list import facts


async def go(bot: main, channel: str, sender: str, args: List[str]):
    if len(args) == 0:
        await bot.message(channel, facts["go_no_args"])
    else:
        await bot.message(channel, f"{', '.join(str(seal) for seal in args)} {facts['go']})")