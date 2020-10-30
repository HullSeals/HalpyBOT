from typing import List
import main
from .message_builder import send_to

async def manual_case(bot: main, channel: str, sender: str, args: List[str]):
    message = f"xxxx MANCASE xxxx\n" \
              f"{' '.join(args)}\n" \
              f"xxxx NEWCASE xxxx"
    for ch in send_to:
        await bot.message(ch, message)

async def manual_kingfisher(bot: main, channel: str, sender: str, args: List[str]):
    message = f"xxxx MANKFCASE xxxx\n" \
              f"{' '.join(args)}\n" \
              f"xxxx NEWKFCASE xxxx"
    for ch in send_to:
        await bot.message(ch, message)