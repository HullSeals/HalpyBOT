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
from typing import Optional

import pydle

from ..announcer import announcer
from ..command import CommandGroup
from ..configmanager import config
from ..database import NoDatabaseConnection, DatabaseConnection

class HalpyBOT(pydle.Client):

    def __init__(self, *args, **kwargs):
        """Initialize a new Pydle client"""
        super().__init__(*args, **kwargs)
        self._commandhandler: Optional[CommandGroup] = None

    @property
    def commandhandler(self):
        """Command/fact handler object that messages are passed to"""
        return self._commandhandler

    @commandhandler.setter
    def commandhandler(self, handler: CommandGroup):
        self._commandhandler = handler

    # Join the Server and Channels and OperLine
    async def on_connect(self):
        """Execute login script

        Called by Pydle on bot startup. Lets the bot join channels
        from config and login with operserv
        """
        await super().on_connect()
        await self.operserv_login()
        for channel in config['Channels']['channellist'].split():
            await self.join(channel)

    async def on_message(self, target, nick, message):
        """Handle an IRC message

        Invoked from Pydle on a new message. Message is passed to
        command handler and announcer.

        Args:
            target (str): Channel message was sent to
            nick (str): Nickname of user who sent the message
            message (str):

        """
        if nick == self.nickname:
            return  # Let's not react to ourselves shall we?

        await super().on_channel_message(target, nick, message)

        # Special command for getting the bot prefix
        if message == f"{self.nickname} prefix":
            return await self.message(target, f"Prefix: {config['IRC']['commandPrefix']}")

        # Pass message to command handler
        if self._commandhandler:
            await self._commandhandler.invoke_from_message(self, target, nick, message)

        # Pass to announcer, to be removed Soon(TM)
        nicks = config['Announcer']['nicks'].split()
        if target in config['Announcer']['channel'].split() and nick in nicks:
            await announcer.handle_announcement(self, target, nick, message)

    async def reply(self, channel: str, sender: str, in_channel: bool, message: str):
        """Reply to a message sent by a user

        All arguments should be present in a Context object created by
        a command handler

        Args:
            channel (str): Channel name the command was invoked in
            sender (str): Command user
            in_channel (bool): True if in a channel, else False
            message (str): Message to be sent

        """
        if in_channel:
            await self.message(channel, message)
        else:
            await self.message(sender, message)

    async def offline_monitor(self):
        """Monitor offline mode

        Initializes a database connection every 5 minutes
        and checks if the bot is online or not. If it concludes
        that a DB connection is not currently available, OM mode
        broadcasting is initiated.

        """
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

    async def operserv_login(self):
        """Log in with OperServ

        Note: a logout command is not currently available
        """
        return await self.raw(f"OPER {config['IRC']['operline']} {config['IRC']['operlinePassword']}\r\n")