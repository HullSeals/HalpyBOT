import main
from typing import List
from modules import commandhandler

from .fact_list import facts

# If the DM-only check somehow fails, allow it to be sent in channels+DM
req_dm = False

async def recite_fact(bot: main, channel: str, sender: str, args: List[str], messagemode: int, fact: str):
    # Check if fact is DM only
    global req_dm
    if str(fact) in commandhandler.factPrivateOnly:
        req_dm = True
    elif str(fact) in commandhandler.factlist:
        req_dm = False
    else:
        msg = "Fact not properly registered! Contact a Cyberseal"
        if messagemode == 1:
            return await bot.message(channel, msg)
        elif messagemode == 2:
            return await bot.message(sender, msg)
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
            return await bot.message(sender, f"{' '.join(str(seal) for seal in args)}{facts[str(fact)]})")
    # PM only, 1 version
    if f"{fact}_no_args" not in facts and messagemode == 2 and req_dm is True:
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
            await bot.message(channel, f"{' '.join(str(seal) for seal in args)}{facts[str(fact)]}")
    elif messagemode == 2:
        if len(args) == 0:
            await bot.message(sender, facts[f"{str(fact)}_no_args"])
        else:
            await bot.message(sender, f"{' '.join(str(seal) for seal in args)}{facts[str(fact)]}")
    else:
        return
