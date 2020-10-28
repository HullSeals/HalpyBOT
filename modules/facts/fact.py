import main
from typing import List

from .fact_list import facts

async def recite_fact(bot: main, channel: str, sender: str, args: List[str], messagemode: int, fact: str):
    if messagemode == 1:
        if len(args) == 0:
            await bot.message(channel, facts[f"{str(fact)}_no_args"])
        else:
            await bot.message(channel, f"{' '.join(str(seal) for seal in args)} {facts[str(fact)]})")
    elif messagemode == 2:
        if len(args) == 0:
            await bot.message(sender, facts[f"{str(fact)}_no_args"])
        else:
            await bot.message(sender, f"{' '.join(str(seal) for seal in args)} {facts[str(fact)]})")
    else:
        return


async def go(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='go')


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
