"""
HalpyBOT v1.4.2

halpybot.py - Pydle client module for HalpyBOT

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import Optional
import logging

import pydle
from ._listsupport import ListHandler

from ..command import Commands, CommandGroup
from ..configmanager import config
from ..facts import Facts
from ..database import NoDatabaseConnection
from ..notice import on_notice as handle_notice

pool = pydle.ClientPool()

class HalpyBOT(pydle.Client, ListHandler):

    def __init__(self, *args, **kwargs):
        """Initialize a new Pydle client"""
        super().__init__(*args, **kwargs)
        self._commandhandler: Optional[CommandGroup] = Commands
        self._commandhandler.facthandler = Facts

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
        try:
            await self._commandhandler.facthandler.fetch_facts(preserve_current=False)
        except NoDatabaseConnection:
            logging.error("Could not fetch facts from DB, backup file loaded and entering OM")
        for channel in config['Channels']['channellist'].split():
            await self.join(channel, force=True)

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

    async def operserv_login(self):
        """Log in with OperServ

        Note: a logout command is not currently available
        """
        return await self.raw(f"OPER {config['IRC']['operline']} {config['IRC']['operlinePassword']}\r\n")

    async def join(self, channel, password=None, force: bool = False):
        """Join a channel

        We do not allow Halpy to join a non-existent channel,
        as this would first create it and thus be a PITA.

        Args:
            channel (str): channel name
            password (str or None): Channel password, optional
            force (bool): join the channel regardless of its existence. Use with
                care, do not include in user-facing functions.

        """
        if not force and channel not in await self.all_channels():
            raise ValueError(f"No such channel: {channel}")
        await super().join(channel, password)
        if channel not in config['Channels']['channellist'].split():
            config['Channels']['channellist'] += f' {channel}'
            with open('config/config.ini', 'w') as conf:
                config.write(conf)

    async def part(self, channel, message=None):
        """Part a channel

        Args:
            channel (str): Channel we want to leave
            message (str): Part message

        """
        await super().part(channel, message)
        chlist = config['Channels']['channellist'].split()
        if channel in chlist:
            chlist.remove(channel)
            config['Channels']['channellist'] = ' '.join(chlist)
            with open('config/config.ini', 'w') as conf:
                config.write(conf)

    async def on_notice(self, target, by, message):
        """Handle an incoming notice

        For security reasons, notices will only be processed when originating
        from whitelisted sources, this should generally be UnrealIRCd, Anope, and
        botadmins for debugging reasons.

        Args:
            target (str): target for the notice
            by (str): client, service, or server sending out the notice
            message (str): Content of the notice

        """
        await handle_notice(self, by, target, message)
