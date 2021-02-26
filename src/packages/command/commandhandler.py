"""
HalpyBOT v1.1

commandhandler.py - Send messages to the correct src

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import src.commands
import src.commands.bot_management.puppet
import src.commands.bot_management.settings
import src.commands.forcejoin.forcejoin
from src.commands.fact.fact import recite_fact
import main
from src.commands.announcer import manual_case
from src.packages.database.facts import fact_index
from src.commands.fact import fact
from src.commands.bot_management import settings, shutdown
from src.commands.delayedboard import delayedboard

commandList = {
    # Announcer commands
    "manualcase": manual_case.cmd_manual_case,
    "mancase": manual_case.cmd_manual_case,
    "manualfish": manual_case.cmd_manual_kingfisher,
    "manfish": manual_case.cmd_manual_kingfisher,
    "wssPing": manual_case.cmd_wss_ping,
    # Util commands
    "shutdown": shutdown.cmd_shutdown,
    "ping": src.commands.cmd_ping,
    "say": src.commands.bot_management.puppet.cmd_say,
    "joinchannel": src.commands.bot_management.settings.cmd_joinchannel,
    "partchannel": src.commands.bot_management.settings.cmd_part,
    "forcejoin": src.commands.forcejoin.forcejoin.cmd_sajoin,
    # Fact management commands
    "allfacts": fact.cmd_allfacts,
    "fact_update": fact.cmd_manual_ufi,
    "ufi": fact.cmd_manual_ufi,
    "addfact": fact.cmd_addfact,
    "deletefact": fact.cmd_deletefact,
    # Settings commands
    "bot_management": settings.cmd_group_settings,
    # Delayed case manager
    "delaycase": delayedboard.cmd_createDelayedCase,
    "reopen": delayedboard.cmd_ReopenDelayedCase,
    "endcase": delayedboard.cmd_closeDelayedCase,
    "close": delayedboard.cmd_closeDelayedCase,
    "updatestatus": delayedboard.cmd_updateDelayedStatus,
    "updatenotes": delayedboard.cmd_updateDelayedNotes,
    "delaystatus": delayedboard.cmd_checkDelayedCases,
    "checkstatus": delayedboard.cmd_checkDelayedCases,
    "updatecase": delayedboard.cmd_updateDelayedCase,
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
