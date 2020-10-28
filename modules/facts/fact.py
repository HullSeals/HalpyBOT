import main
from typing import List

from .fact_list import facts


async def go(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    if messagemode == 1:
        if len(args) == 0:
            await bot.message(channel, facts["go_no_args"])
        else:
            await bot.message(channel, f"{' '.join(str(seal) for seal in args)} {facts['go']})")
    elif messagemode == 2:
        if len(args) == 0:
            await bot.message(sender, facts["go_no_args"])
        else:
            await bot.message(sender, f"{' '.join(str(seal) for seal in args)} {facts['go']})")
    else:
        return


async def help(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    if messagemode == 1:
        return
    if messagemode == 2:
        await bot.message(sender, facts["help"])


async def about(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    if messagemode == 1:
        return
    if messagemode == 2:
        await bot.message(sender, facts["about"])


async def bacon(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    if messagemode == 1:
        await bot.message(channel, facts["bacon"])
    if messagemode == 2:
        await bot.message(sender, facts["bacon"])
