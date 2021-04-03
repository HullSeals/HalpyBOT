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

from src import config, DatabaseConnection, NoDatabaseConnection, CommandGroup
from src.packages.announcer import announcer
from src.packages.database import facts

channels = config['Channels']['ChannelList'].split()
om_channels = config['Offline Mode']['announce_channels'].split()


class HalpyBOT(pydle.Client):
    """Halpy IRC client, subclassed from pydle """

    _version: str = "Unknown"
    _prefix: str = None
    _oper: bool = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Function we send command messages to
        self._commandhandler = CommandGroup.invoke_from_message
        self._announcer = announcer.announce
        logging.info("CLIENT: Command handler + announcer"
                     "started and ready to go.")

    @property
    def version(self):
        """Bot version"""
        return self._version

    @version.setter
    def version(self, version: str):
        self._version = version

    @property
    def prefix(self):
        """Prefix for commands and facts"""
        return self._prefix

    @prefix.setter
    def prefix(self, prefix: str):
        if not len(prefix) == 1:
            raise ValueError("Prefix must be one character")
        self._prefix = prefix

    @property
    def oper(self):
        """OS Login

        Returns bot setting for operserv. To get the actual IRC operator
        status run a whois on the bot itself instead.

        Returns:
            (bool): True if setting is True... You get the point.

        """
        return self._oper

    @oper.setter
    async def oper(self, enable: bool):
        """Set IRC operator status for the bot

        CAUTION: Logout will raise an NotImplementedError for now.

        Args:
            enable (bool): Login if True, else logout

        """
        if enable:
            await self.raw(f"OPER {config['IRC']['operline']} {config['IRC']['operlinePassword']}\r\n")
        else:
            # TODO add OS logout
            raise NotImplementedError

    async def on_connect(self):
        await super().on_connect()
        logging.info("CLIENT: Connection to server established.")
        await facts.get_facts(startup=True)
        for channel in channels:
            await self.join(channel)
            logging.info(f"Joining {channel}")
        await self.offline_monitor()

    async def on_message(self, target, nick, message):
        await super().on_channel_message(target, nick, message)

        if message == f"{self.nickname} prefix":
            return await self.message(target, f"Prefix: {self._prefix}")

        # If prefixed, send to command handler
        if message.startswith(self._prefix):
            await self._commandhandler(self, target, nick, message)

        # If possible announcement, send to handler
        nicks = config['Announcer']['nicks'].split()
        if target in config['Announcer']['channel'] and nick in nicks:
            await self._announcer(self, target, nick, message)

    async def reply(self, channel: str, sender: str, in_channel: bool, message: str):
        """Reply to a message in IRC

        If the message was sent from a channel, send to the same channel. Else, send to user

        Args:
            channel (str): Channel name
            sender (str): User nickname
            in_channel (bool): True if in a channel, else False
            message (str): Message to be sent

        """
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
