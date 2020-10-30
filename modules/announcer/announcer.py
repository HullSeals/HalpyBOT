import pydle
import main
from config import Announcer
from . import message_builder as mb

caseIndicatorsList = {
    "CODEBLACK": mb.codeblack,
    "PC": mb.pc
}

async def on_channel_message(bot: main, channel: str, sender: str, message: str):
    # Double-check if channel and nick are correct
    if channel in Announcer.channels and sender in Announcer.nicks:
        # Seperate arguments
        parts = message.split(" -~~- ")
        casetype = parts[0]
        args = parts[1:]
        if casetype in caseIndicatorsList:
            return await caseIndicatorsList[casetype](bot, channel, sender, args)
        else:
            return
