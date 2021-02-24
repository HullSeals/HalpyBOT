"""
HalpyBOT v1.1

commandhandler.py - Send messages to the correct src

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from src.facts.fact import recite_fact
import main
from .announcer import manual_case
from .util import shutdown, utils
from src.database.facts import fact_index
from src.facts import fact
from src.botsettings import settings
from src.delayedboard import delayed


commandList = {
    # Announcer commands
    "manualcase": manual_case.cmd_manual_case,
    "mancase": manual_case.cmd_manual_case,
    "manualfish": manual_case.cmd_manual_kingfisher,
    "manfish": manual_case.cmd_manual_kingfisher,
    "wssPing": manual_case.cmd_wss_ping,
    # Util commands
    "shutdown": shutdown.cmd_shutdown,
    "ping": utils.cmd_ping,
    "say": utils.cmd_say,
    "test_command": utils.cmd_test,
    "joinchannel": utils.cmd_joinchannel,
    "partchannel": utils.cmd_part,
    "forcejoin": utils.cmd_sajoin,
    # Fact management commands
    "allfacts": fact.cmd_allfacts,
    "fact_update": fact.cmd_manual_ufi,
    "ufi": fact.cmd_manual_ufi,
    "addfact": fact.cmd_addfact,
    "deletefact": fact.cmd_deletefact,
    # Settings commands
    "settings": settings.cmd_group_settings,
    # Delayed case manager
    "delaycase": delayed.cmd_createDelayedCase,
    "reopen": delayed.cmd_ReopenDelayedCase,
    "endcase": delayed.cmd_closeDelayedCase,
    "close": delayed.cmd_closeDelayedCase,
}

class Context:
    def __init__(self, bot: main, channel: str, sender: str, in_channel: bool):
        self.bot = bot
        self.channel = channel
        self.sender = sender
        self.in_channel = in_channel

    async def reply(self, message: str):
        await self.bot.reply(self.channel, self.sender, self.in_channel, message)


async def on_channel_message(bot: main, channel: str, sender: str, message: str):
    if message.startswith(main.config['IRC']['commandPrefix']):
        parts = message[1:].split(" ")
        command = parts[0].lower()
        args = parts[1:]
        in_channel = True
        ctx = Context(bot, channel, sender, in_channel)
        if command in commandList:
            return await commandList[command](ctx, args)
        elif command in fact_index:
            return await recite_fact(ctx, args, fact=str(command))
        else:
            return


async def on_private_message(bot: main, channel: str, sender: str, message: str):
    if message.startswith(main.config['IRC']['commandPrefix']):
        parts = message[1:].split(" ")
        command = parts[0].lower()
        args = parts[1:]
        in_channel = False
        ctx = Context(bot, channel, sender, in_channel)
        if command in commandList.keys():
            return await commandList[command](ctx, args)
        elif command in fact_index:
            return await recite_fact(ctx, args, fact=str(command))
        else:
            return
