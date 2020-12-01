"""
HalpyBOT v1.1

announcer.py - Client announcement handler

Copyright (c) 2020 The Hull Seals,
All rights reserved

Licensed under the GNU General Public License
See license.md
"""


import main
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
    # Seperate arguments
    parts = message.split(" -~~- ")
    if parts[0] == "PPWK":
        args = parts[1:]
        ctx = AnnouncerContext(bot, channel, sender)
        logging.info(f"Paperwork Completion from {sender}: {message}")
        return await mb.ppwk(ctx, args)
    else:
        casetype = parts[0]
        args = parts[1:]
        ctx = AnnouncerContext(bot, channel, sender)
        if casetype in caseIndicatorsList:
            logging.info(f"NEW ANNOUNCER WEBHOOK PAYLOAD FROM {sender}: {message}")
            return await caseIndicatorsList[casetype](ctx, args)
        else:
            return
