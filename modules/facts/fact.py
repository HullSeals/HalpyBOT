import main
from typing import List

from .fact_list import facts


async def recite_fact(bot: main, channel: str, sender: str, args: List[str], in_channel: bool, fact: str):
    # Check if fact is DM only
    req_dm = False
    if facts[str(fact)][0] is True:
        req_dm = True
    elif facts[str(fact)][0] is False:
        req_dm = False
    else:
        msg = "Fact not properly registered! Contact a Cyberseal"
        if in_channel:
            return await bot.message(channel, msg)
        elif in_channel is False:
            return await bot.message(sender, msg)
    # Check if fact is present
    if str(fact) not in facts:
        msg = "Couldn't find fact! contact a Cyberseal"
        if in_channel:
            return await bot.message(channel, msg)
        elif in_channel is False:
            return await bot.message(sender, msg)
    # PM only, noargs and args
    if f"{fact}_no_args" in facts and in_channel is False and req_dm is True:
        if len(args) == 0:
            return await bot.message(sender, facts[str(f"{fact}_no_args")][1])
        else:
            return await bot.message(sender, f"{' '.join(str(seal) for seal in args)}{facts[str(fact)][1]})")
    # PM only, 1 version
    if f"{fact}_no_args" not in facts and in_channel is False and req_dm is True:
        return await bot.message(sender, facts[str(fact)])
    # Public and PM, 1 version
    if f"{fact}_no_args" not in facts and req_dm is False:
        if in_channel:
            return await bot.message(channel, facts[str(fact)][1])
        else:
            return await bot.message(sender, facts[str(fact)][1])
    # Public and PM, args and noargs
    if in_channel and req_dm is False:
        if len(args) == 0:
            await bot.message(channel, facts[f"{str(fact)}_no_args"][1])
        else:
            await bot.message(channel, f"{' '.join(str(seal) for seal in args)}{facts[str(fact)][1]}")
    elif in_channel is False:
        if len(args) == 0:
            await bot.message(sender, facts[f"{str(fact)}_no_args"])
        else:
            await bot.message(sender, f"{' '.join(str(seal) for seal in args)}{facts[str(fact)][1]}")
    else:
        return
