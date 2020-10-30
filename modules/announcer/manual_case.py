from typing import List
import main
from ..checks import require_permission, DeniedMessage

send_to = ["#Repair-Requests", "#Code-Black", "#seal-bob"]

@require_permission("DRILLED", message=DeniedMessage.DRILLED)
async def manual_case(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    if messagemode == 1:
        message = f"xxxx MANCASE xxxx\n" \
                  f"{' '.join(args)}\n" \
                  f"xxxx NEWCASE xxxx"
        for ch in send_to:
            await bot.message(ch, message)
    else:
        return

@require_permission("DRILLED", message=DeniedMessage.DRILLED)
async def manual_kingfisher(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    if messagemode == 1:
        message = f"xxxx MANKFCASE xxxx\n" \
                  f"{' '.join(args)}\n" \
                  f"xxxx NEWKFCASE xxxx"
        for ch in send_to:
            await bot.message(ch, message)
    else:
        return
