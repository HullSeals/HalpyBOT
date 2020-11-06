import main
from ..util.checks import require_permission, DeniedMessage, require_dm
from .fact import factlist
from typing import List

@require_dm()
@require_permission(req_level="PUP", message=DeniedMessage.PUP)
async def allfacts(bot: main, channel: str, sender: str, args: List[str], in_channel: bool):
    listallfacts = f"{', '.join(str(fact) for fact in factlist)}"
    await bot.reply(channel, sender, in_channel, listallfacts)
