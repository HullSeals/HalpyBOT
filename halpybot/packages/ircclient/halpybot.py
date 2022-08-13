"""
halpybot.py - Pydle client module for HalpyBOT

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import asyncio
import os
import signal
from typing import Optional
import pydle
from loguru import logger
from .. import notify
from ..configmanager import config_write, config
from ._listsupport import ListHandler
from ..command import Commands, CommandGroup
from ..facts import Facts
from ..database import NoDatabaseConnection


pool = pydle.ClientPool()


class HalpyBOT(pydle.Client, ListHandler):
    """Create the instance of HalpyBOT,"""

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

    # Pydle has a problem where ConnectionResetErrors zombify the bot, and it won't attempt to recover.
    # If this happens, the bot should promptly text a Cyber and then shutdown. Systemctl will attempt to
    # restart the bot from the top.
    # Issue Ref: https://github.com/Shizmob/pydle/issues/155
    # FIXME: For the love of Halpy Pydle please fix this.
    async def handle_forever(self):
        try:
            await super().handle_forever()
        except ConnectionResetError as cre:
            logger.exception("HalpyBOT has crashed with a CRE.")
            await crash_notif("Connection Reset Error", cre)

    # Sometimes, the bot will fail in its attempts to reconnect with a CAE
    async def _disconnect(self, expected):
        try:
            await super()._disconnect(expected)
        except ConnectionAbortedError as cae:
            logger.exception("HalpyBOT has crashed with a CAE.")
            await crash_notif("Connection Aborted Error", cae)

    # Handle the clean disconnect but fail to reconnect of the bot
    async def on_disconnect(self, expected):
        await super().on_disconnect(expected)
        if self._reconnect_attempts >= self.RECONNECT_MAX_ATTEMPTS:
            await crash_notif(
                "exceeding reconnection attempt maximum",
                "on_disconnect max attempts reached",
            )

    # End Crash Detection

    # Join the Server and Channels and OperLine
    async def on_connect(self):
        """Execute login script

        Called by Pydle on bot startup. Lets the bot join channels
        from config and login with operserv
        """
        await super().on_connect()
        await self.operserv_login()
        if config.getboolean("System Monitoring", "failure_button"):
            config_write("System Monitoring", "failure_button", "False")
        try:
            await self._commandhandler.facthandler.fetch_facts(preserve_current=False)
        except NoDatabaseConnection:
            logger.error(
                "Could not fetch facts from DB, backup file loaded and entering OM"
            )
        for channel in config["Channels"]["channellist"].split():
            await self.join(channel, force=True)

    async def on_message(self, target, by, message):
        """Handle an IRC message

        Invoked from Pydle on a new message. Message is passed to
        command handler and announcer.

        Args:
            target (str): Channel message was sent to
            by (str): Nickname of user who sent the message.
            message (str):

        """
        if by == self.nickname:
            return  # Let's not react to ourselves shall we?

        await super().on_channel_message(target, by, message)

        # Special command for getting the bot prefix
        if message == f"{self.nickname} prefix":
            return await self.message(
                target, f"Prefix: {config['IRC']['commandPrefix']}"
            )

        # Pass message to command handler
        if self._commandhandler:
            await self._commandhandler.invoke_from_message(self, target, by, message)

    async def reply(self, channel: str, sender: str, in_channel: bool, message: str):
        """Reply to a message sent by a user

        All arguments should be present in a Context object created by
        a command handler

        Args:
            channel (str): Channel the command was invoked in
            sender (str): Command user
            in_channel (bool): True if in a channel, else False
            message (str): Message to be sent

        """
        if in_channel:
            await self.message(channel, message)
        else:
            await self.message(sender, message)

    async def on_unknown(self, message):
        """Unknown Command"""
        logger.warning(f"Unknown Command Received: {message}")

    async def operserv_login(self):
        """Log in with OperServ

        Note: a logout command is not currently available
        """
        return await self.raw(
            f"OPER {config['IRC']['operline']} {config['IRC']['operlinePassword']}\r\n"
        )

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
        if channel not in config["Channels"]["channellist"].split():
            config["Channels"]["channellist"] += f" {channel}"
            with open("config/config.ini", "w", encoding="UTF-8") as conf:
                config.write(conf)

    async def part(self, channel, message=None):
        """Part a channel

        Args:
            channel (str): Channel we want to leave
            message (str): Part message

        """
        await super().part(channel, message)
        chlist = config["Channels"]["channellist"].split()
        if channel in chlist:
            chlist.remove(channel)
            config["Channels"]["channellist"] = " ".join(chlist)
            with open("config/config.ini", "w", encoding="UTF-8") as conf:
                config.write(conf)


client = HalpyBOT(
    nickname=config["IRC"]["nickname"],
    sasl_identity=config["SASL"]["identity"],
    sasl_password=config["SASL"]["password"],
    sasl_username=config["SASL"]["username"],
    eventloop=asyncio.get_event_loop(),
)


async def crash_notif(crashtype, condition):
    """
    Send a notification to the staff in the event of a failure in the bot.

    Args:
        crashtype (str): The type of incident being reported.
        condition: The error being reported that is preventing the bot from starting.

    Returns:
        Nothing.
    """
    if config.getboolean("System Monitoring", "failure_button"):
        logger.critical(
            "HalpyBOT has failed, but this incident has already been reported."
        )
    else:
        subject = "HalpyBOT has died!"
        topic = config["Notify"]["cybers"]
        message = f"HalpyBOT has shut down due to {crashtype}. Investigate immediately. Error Text: {condition}"
        try:
            await notify.send_notification(topic, message, subject)
            # Only trip the fuse if a notification is passed
            config_write("System Monitoring", "failure_button", "True")
        except notify.NotificationFailure:
            logger.exception("Unable to send the notification!")
    logger.critical(
        "{crashtype} detected. Shutting down for my own protection! {condition}",
        crashtype=crashtype,
        condition=condition,
    )
    os.kill(os.getpid(), signal.SIGTERM)
