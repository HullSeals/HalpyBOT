import main
from typing import List

from .fact_list import facts

async def recite_fact(bot: main, channel: str, sender: str, args: List[str], messagemode: int, fact: str,
                      req_dm):
    # Check if fact is present
    if str(fact) not in facts:
        msg = "Couldn't find fact! contact a Cyberseal"
        if messagemode == 1:
            return await bot.message(channel, msg)
        elif messagemode == 2:
            return await bot.message(sender, msg)
    # PM only, noargs and args
    if f"{fact}_no_args" in facts and messagemode == 2 and req_dm is True:
        if len(args) == 0:
            return await bot.message(sender, facts[str(f"{fact}_no_args")])
        else:
            return await bot.message(sender, f"{', '.join(str(seal) for seal in args)} {facts[str(fact)]})")
    # PM only, 1 version
    if f"{fact}_no_args" not in facts and messagemode == 2 and req_dm is True:
        print("Help sent")
        return await bot.message(sender, facts[str(fact)])
    # Public and PM, 1 version
    if f"{fact}_no_args" not in facts and req_dm is False:
        if messagemode == 1:
            return await bot.message(channel, facts[str(fact)])
        else:
            return await bot.message(sender, facts[str(fact)])
    # Public and PM, args and noargs
    if messagemode == 1 and req_dm is False:
        if len(args) == 0:
            await bot.message(channel, facts[f"{str(fact)}_no_args"])
        else:
            await bot.message(channel, f"{', '.join(str(seal) for seal in args)} {facts[str(fact)]})")
    elif messagemode == 2:
        if len(args) == 0:
            await bot.message(sender, facts[f"{str(fact)}_no_args"])
        else:
            await bot.message(sender, f"{', '.join(str(seal) for seal in args)} {facts[str(fact)]})")
    else:
        return


# ----- START FACTS -----

async def go(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='go', req_dm=False)

async def help(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='help', req_dm=True)

async def about(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='about', req_dm=True)

async def bacon(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='bacon', req_dm=False)
