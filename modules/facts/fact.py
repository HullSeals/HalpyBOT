import main
from typing import List
from modules import commandhandler

from .fact_list import facts

# If the DM-only check somehow fails, allow it to be sent in channels+DM
req_dm = False

async def recite_fact(bot: main, channel: str, sender: str, args: List[str], messagemode: int, fact: str):
    # Check if fact is DM only
    global req_dm
    if str(fact) in commandhandler.commandPrivateOnly:
        req_dm = True
    elif str(fact) in commandhandler.commandList:
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
            return await bot.message(sender, f"{', '.join(str(seal) for seal in args)} {facts[str(fact)]})")
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
            await bot.message(channel, f"{', '.join(str(seal) for seal in args)} {facts[str(fact)]}")
    elif messagemode == 2:
        if len(args) == 0:
            await bot.message(sender, facts[f"{str(fact)}_no_args"])
        else:
            await bot.message(sender, f"{', '.join(str(seal) for seal in args)} {facts[str(fact)]}")
    else:
        return


# ----- START FACTS -----

async def about(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='about')

async def go(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='go')

async def beacon(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='beacon')

async def cbinfo(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='cbinfo')

async def cbmining(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='cbmining')

async def clientinfo(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='clientinfo')

async def escapeneutron(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='escapeneutron')

async def paperwork(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='paperwork')

async def pcfr(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='pcfr')

async def psfr(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='psfr')

async def xbfr(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='xbfr')

async def wing(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='wing')

async def stuck(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='stuck')

async def prep(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='prep')

async def verify(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='verify')

async def chatter(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='chatter')

async def join(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='join')

async def bacon(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='bacon')

async def fuel(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='fuel')

async def cmdlist(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='cmdlist')

async def welcome(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='welcome')

async def tos(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='tos')

async def highg(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='highg')

async def synth(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='synth')

async def fact_test(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='fact_test')

async def help(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await recite_fact(bot, channel, sender, args, messagemode, fact='help')