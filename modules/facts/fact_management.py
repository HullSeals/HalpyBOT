import main
from ..util.checks import require_permission, DeniedMessage, require_dm
from .fact import fact_index, update_fact_index, basic_facts
from typing import List
import logging
from .fact import add_fact

@require_dm()
@require_permission(req_level="PUP", message=DeniedMessage.PUP)
async def allfacts(bot: main, channel: str, sender: str, args: List[str], in_channel: bool):
    listallfacts = f"{', '.join(str(fact) for fact in basic_facts)}"
    await bot.reply(channel, sender, in_channel, listallfacts)

@require_permission(req_level="CYBER", message=DeniedMessage.CYBER)
async def manual_ufi(bot: main, channel: str, sender: str, args: List[str], in_channel: bool):
    # TODO run: get facts from database
    logging.info(f"FACT INDEX UPDATE by {sender}")
    await bot.reply(channel, sender, in_channel, "Clearing fact index...")
    fact_index.clear()
    await bot.reply(channel, sender, in_channel, "Updating...")
    await update_fact_index()
    await bot.reply(channel, sender, in_channel, "Done.")


@require_permission(req_level="ADMIN", message=DeniedMessage.ADMIN)
async def addfact(bot: main, channel: str, sender: str, args: List[str], in_channel: bool):
    # TODO Check if already a fact or command, if yes, gracefully exit
    factname = args[0]
    if args[1] == "--dm":
        reqdm = True
        facttext = ' '.join(arg for arg in args[2:])
    else:
        reqdm = False
        facttext = ' '.join(arg for arg in args[1:])
    await add_fact(factname, facttext, sender, reqdm)


# TODO !delete_fact
