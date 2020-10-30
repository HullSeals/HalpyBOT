from . import announcer
import main
from typing import List

async def codeblack(bot: main, channel: str, sender: str, args: List[str]):
    send_to = ["#Repair-Requests", "#Code-Black", "#seal-bob"]
    message = f"xxxx CBCASE xxxx \n" \
              f"CMDR: {args[0]} -- Platform: {args[1]} System: {args[2]} -- Hull: {args[3]} \n" \
              f"Can synth: {args[4]} -- O2 timer: {args[5]} \n" \
              f"xxxx NEWCASE xxxx"
    for ch in send_to:
        await bot.message(ch, message)