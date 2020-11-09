import main
from ..util.checks import require_permission, DeniedMessage, require_dm
from .fact import update_fact_index, basic_facts, get_facts
from typing import List
import logging
from .fact import add_fact, remove_fact, clear_facts

@require_dm()
@require_permission(req_level="PUP", message=DeniedMessage.PUP)
async def allfacts(bot: main, channel: str, sender: str, args: List[str], in_channel: bool):
    listallfacts = f"{', '.join(str(fact) for fact in basic_facts)}"
    await bot.reply(channel, sender, in_channel, listallfacts)

@require_permission(req_level="CYBER", message=DeniedMessage.CYBER)
async def manual_ufi(bot: main, channel: str, sender: str, args: List[str], in_channel: bool):
    logging.info(f"FACT INDEX UPDATE by {sender}")
    await bot.reply(channel, sender, in_channel, "Defenestrating facts...")
    await bot.reply(channel, sender, in_channel, "Clearing fact index...")
    await clear_facts()
    await bot.reply(channel, sender, in_channel, "Fetching facts...")
    await get_facts()
    await bot.reply(channel, sender, in_channel, "Updating...")
    await update_fact_index()
    await bot.reply(channel, sender, in_channel, "Done.")


@require_permission(req_level="ADMIN", message=DeniedMessage.ADMIN)
async def addfact(bot: main, channel: str, sender: str, args: List[str], in_channel: bool):
    factname = args[0]
    if args[1] == "--dm":
        reqdm = True
        facttext = ' '.join(arg for arg in args[2:])
    else:
        reqdm = False
        facttext = ' '.join(arg for arg in args[1:])
    await add_fact(bot, factname, facttext, sender, reqdm, channel, sender, in_channel)


@require_permission(req_level="ADMIN", message=DeniedMessage.ADMIN)
async def deletefact(bot: main, channel: str, sender: str, args: List[str], in_channel: bool):
    factname = args[0]
    await remove_fact(bot, factname, channel, sender, in_channel)
