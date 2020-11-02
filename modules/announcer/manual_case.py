from typing import List
import main
from modules.util.checks import require_permission, DeniedMessage
import logging

send_to = ["#Repair-Requests", "#Code-Black", "#seal-bob"]

@require_permission("DRILLED", message=DeniedMessage.DRILLED)
async def manual_case(bot: main, channel: str, sender: str, args: List[str], in_channel: bool):
    if in_channel:
        message = f"xxxx MANCASE xxxx\n" \
                  f"{' '.join(args)}\n" \
                  f"xxxx NEWCASE xxxx"
        for ch in send_to:
            await bot.message(ch, message)
            logging.info(f"Manual case by {sender} in {channel}: {args}")
    else:
        return

@require_permission("DRILLED", message=DeniedMessage.DRILLED)
async def manual_kingfisher(bot: main, channel: str, sender: str, args: List[str], in_channel: bool):
    if in_channel:
        message = f"xxxx MANKFCASE xxxx\n" \
                  f"{' '.join(args)}\n" \
                  f"xxxx NEWKFCASE xxxx"
        for ch in send_to:
            await bot.message(ch, message)
            logging.info(f"Manual kingfisher case by {sender} in {channel}: {args}")
    else:
        return
