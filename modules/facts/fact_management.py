import main
from ..util.checks import require_permission, DeniedMessage, require_dm
from .fact import fact_index, update_fact_index
from typing import List
import logging

@require_dm()
@require_permission(req_level="PUP", message=DeniedMessage.PUP)
async def allfacts(bot: main, channel: str, sender: str, args: List[str], in_channel: bool):
    # TODO make sure we don't print facts with a language
    listallfacts = f"{', '.join(str(fact) for fact in fact_index)}"
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


# TODO !add_fact

# TODO !delete_fact
