import main
from typing import List

send_to = ["#Repair-Requests", "#Code-Black", "#seal-bob"]

async def codeblack(bot: main, channel: str, sender: str, args: List[str]):
    message = f"xxxx CBCASE xxxx \n" \
              f"CMDR: {args[0]} -- Platform: {args[1]} System: {args[2]} -- Hull: {args[3]} \n" \
              f"Can synth: {args[4]} -- O2 timer: {args[5]} \n" \
              f"xxxx NEWCASE xxxx"
    for ch in send_to:
        await bot.message(ch, message)

async def pc(bot: main, channel: str, sender: str, args: List[str]):
    message = f"xxxx PCCASE xxxx \n" \
              f"CMDR: {args[0]} -- Platform: {args[1]} \n" \
              f"System: {args[2]} -- Hull: {args[3]} \n" \
              f"xxxx NEWCASE xxxx"
    for ch in send_to:
        await bot.message(ch, message)

async def xb(bot: main, channel: str, sender: str, args: List[str]):
    message = f"xxxx XBCASE xxxx \n" \
              f"CMDR: {args[0]} -- Platform: {args[1]} \n" \
              f"System: {args[2]} -- Hull: {args[3]} \n" \
              f"xxxx NEWCASE xxxx"
    for ch in send_to:
        await bot.message(ch, message)

async def ps(bot: main, channel: str, sender: str, args: List[str]):
    message = f"xxxx PSCASE xxxx \n" \
              f"CMDR: {args[0]} -- Platform: {args[1]} \n" \
              f"System: {args[2]} -- Hull: {args[3]} \n" \
              f"xxxx NEWCASE xxxx"
    for ch in send_to:
        await bot.message(ch, message)

async def plterr(bot: main, channel: str, sender: str, args: List[str]):
    message = f"xxxx PLATFORM_ERROR xxxx \n" \
              f"CMDR: {args[0]} -- Platform: {args[1]} \n" \
              f"System: {args[2]} -- Hull: {args[3]} \n" \
              f"xxxx NEWCASE xxxx"
    for ch in send_to:
        await bot.message(ch, message)

async def kingfisher_xb(bot: main, channel: str, sender: str, args: List[str]):
    message = f"xxxx XBKFCASE xxxx\n" \
              f"CMDR: {args[0]} -- Platform: {args[1]}\n" \
              f"System: {args[2]} -- Planet: {args[3]}\n" \
              f"Coordinates: {args[4]}\n" \
              f"Type: {args[5]}\n" \
              f"xxxx NEWCASE xxxx"
    for ch in send_to:
        await bot.message(ch, message)

async def kingfisher_pc(bot: main, channel: str, sender: str, args: List[str]):
    message = f"xxxx PCKFCASE xxxx\n" \
              f"CMDR: {args[0]} -- Platform: {args[1]}\n" \
              f"System: {args[2]} -- Planet: {args[3]}\n" \
              f"Coordinates: {args[4]}\n" \
              f"Type: {args[5]}\n" \
              f"xxxx NEWCASE xxxx"
    for ch in send_to:
        await bot.message(ch, message)

async def kingfisher_ps(bot: main, channel: str, sender: str, args: List[str]):
    message = f"xxxx PSKFCASE xxxx\n" \
              f"CMDR: {args[0]} -- Platform: {args[1]}\n" \
              f"System: {args[2]} -- Planet: {args[3]}\n" \
              f"Coordinates: {args[4]}\n" \
              f"Type: {args[5]}\n" \
              f"xxxx NEWCASE xxxx"
    for ch in send_to:
        await bot.message(ch, message)

async def kingfisher_plterr(bot: main, channel: str, sender: str, args: List[str]):
    message = f"xxxx PLATFORM_ERROR xxxx\n" \
              f"CMDR: {args[0]} -- Platform: {args[1]}\n" \
              f"System: {args[2]} -- Planet: {args[3]}\n" \
              f"Coordinates: {args[4]}\n" \
              f"Type: {args[5]}\n" \
              f"xxxx NEWCASE xxxx"
    for ch in send_to:
        await bot.message(ch, message)
