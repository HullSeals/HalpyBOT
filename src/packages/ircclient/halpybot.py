"""
HalpyBOT v1.4

halpybot.py - Pydle client module for HalpyBOT

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import asyncio
import logging

import pydle

from ..announcer import announcer
from ..command import Facts, Commands
from ..configmanager import config
from ..database import NoDatabaseConnection, DatabaseConnection

class HalpyBOT(pydle.Client):

    # Join the Server and Channels and OperLine
    async def on_connect(self):
        from src import commands
        await super().on_connect()
        try:
            await Facts.fetch_facts(preserve_current=False)
        except NoDatabaseConnection:
            logging.error("FACTS: Loading facts from offline file, entering offline mode.")
        print("Fact module loaded successfully")
        await self.raw(f"OPER {config['IRC']['operline']} {config['IRC']['operlinePassword']}\r\n")
        logging.info("Connected")
        print("Connected!")
        for channel in config['Channels']['channellist'].split():
            await self.join(channel)
            logging.info(f"Joining {channel}")
        await self.offline_monitor()

    async def on_message(self, target, nick, message):

        if nick == self.nickname:
            return  # Let's not react to ourselves shall we?
        await super().on_channel_message(target, nick, message)

        if message == f"{self.nickname} prefix":
            return await self.message(target, f"Prefix: {config['IRC']['commandPrefix']}")

        await Commands.invoke_from_message(self, target, nick, message)

        nicks = config['Announcer']['nicks'].split()
        if target in config['Announcer']['channel'].split() and nick in nicks:
            await announcer.handle_announcement(self, target, nick, message)

    async def reply(self, channel: str, sender: str, in_channel: bool, message: str):
        if in_channel:
            await self.message(channel, message)
        else:
            await self.message(sender, message)

    # FIXME this works for now but take a look at this when time allows.
    async def offline_monitor(self):
        logging.debug("STARTING OFFLINECHECK")
        try:
            loop = asyncio.get_running_loop()
            while True:
                if config['Offline Mode']['enabled'] == 'True' and \
                   config['Offline Mode']['warning override'] == 'False':
                    for ch in config['Offline Mode']['announce_channels'].split():
                        await self.message(ch, "HalpyBOT in OFFLINE mode! Database connection unavailable. "
                                               "Contact a CyberSeal.")
                await asyncio.sleep(300)
                if config['Offline Mode']['enabled'] == 'False':
                    # We only need to start the connection, DatabaseConnection will trip the CB if neccesary
                    try:
                        with DatabaseConnection() as db:
                            db.ping()
                    except NoDatabaseConnection:
                        continue
                    await asyncio.sleep(300)
        except asyncio.exceptions.CancelledError:
            pass
