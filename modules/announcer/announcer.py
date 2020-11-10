import main
from config import Announcer
from . import message_builder as mb
import logging


caseIndicatorsList = {
    "CODEBLACK": mb.codeblack,
    "PC": mb.pc,
    "XB": mb.xb,
    "PS4": mb.ps,
    "PLTERR": mb.plterr,
    "XBFISH": mb.kingfisher_xb,
    "PCFISH": mb.kingfisher_pc,
    "PSFISH": mb.kingfisher_ps,
    "PLTERRFISH": mb.kingfisher_plterr
}

class AnnouncerContext:
    def __init__(self, bot: main, channel: str, sender: str):
        self.bot = bot
        self.channel = channel
        self.sender = sender

async def on_channel_message(bot: main, channel: str, sender: str, message: str):
    # Double-check if channel and nick are correct
    if channel in Announcer.channels and sender in Announcer.nicks:
        # Seperate arguments
        parts = message.split(" -~~- ")
        casetype = parts[0]
        args = parts[1:]
        ctx = AnnouncerContext(bot, channel, sender)
        if casetype in caseIndicatorsList:
            logging.info(f"NEW ANNOUNCER WEBHOOK PAYLOAD FROM {sender}: {message}")
            return await caseIndicatorsList[casetype](ctx, args)
        else:
            return
