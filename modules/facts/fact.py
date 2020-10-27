import main
from typing import List

from .fact_list import facts

#TODO - Check how message came in, give output accordingly. Allow DM-d regular messages to be DM'd.
# Check message(sender vs message(channel in the response for format. Not making more entries until this is sorted.

#TODO- Think about a length limit on the commands? ex, # of chars before it ignores?

async def go(bot: main, channel: str, sender: str, args: List[str]):
    if len(args) == 0:
        await bot.message(channel, facts["go_no_args"])
    else:
        await bot.message(channel, f"{' '.join(str(seal) for seal in args)} {facts['go']})")

async def help(bot: main, channel: str, sender: str, args: List[str]):
    await bot.message(sender, facts["help"])

async def about(bot: main, channel: str, sender: str, args: List[str]):
    await bot.message(sender, facts["about"])

async def bacon(bot: main, channel: str, sender: str, args: List[str]):
        await bot.message(channel, facts["bacon"])
