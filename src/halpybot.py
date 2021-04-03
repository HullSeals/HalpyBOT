"""
HalpyBOT v1.4

halpybot.py - Pydle client for IRC interaction

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import asyncio
import logging

import pydle

from src import config, CommandGroup, DatabaseConnection, NoDatabaseConnection
from src.packages.announcer import announcer
from src.packages.database import facts

channels = config['Channels']['ChannelList'].split()
om_channels = config['Offline Mode']['announce_channels'].split()


class HalpyBOT(pydle.Client):
    """Halpy IRC client, subclassed from pydle """

    _version: str = "Unknown"

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, version: str):
        self._version = version

    async def on_connect(self):
        await super().on_connect()
        await facts.on_connect()
        print("Fact module loaded successfully")
        await self.raw(f"OPER {config['IRC']['operline']} {config['IRC']['operlinePassword']}\r\n")
        logging.info("Connected")
        print("Connected!")
        for channel in channels:
            await self.join(channel)
            logging.info(f"Joining {channel}")
        await self.offline_monitor()

    async def on_message(self, target, nick, message):
        await super().on_channel_message(target, nick, message)
        if message == f"{self.nickname} prefix":
            return await self.message(target, f"Prefix: {config['IRC']['commandPrefix']}")
        await CommandGroup.invoke_from_message(self, target, nick, message)
        nicks = [entry.strip() for entry in config.get('Announcer', 'nicks').split(',')]
        if target in config['Announcer']['channel'] and nick in nicks:
            await announcer.on_channel_message(self, target, nick, message)

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
                    for ch in om_channels:
                        await self.message(ch, "HalpyBOT in OFFLINE mode! Database connection unavailable. "
                                               "Contact a CyberSeal.")
                await asyncio.sleep(300)
                if config['Offline Mode']['enabled'] == 'False':
                    # We only need to start the connection, DatabaseConnection will trip the CB if neccesary
                    try:
                        DatabaseConnection()
                    except NoDatabaseConnection:
                        continue
                    await asyncio.sleep(300)
        except asyncio.exceptions.CancelledError:
            pass
