"""
context.py - Message context object

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from __future__ import annotations
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..ircclient import HalpyBOT


class Context:
    """Message context object"""

    def __init__(
        self,
        bot: HalpyBOT,
        channel: str,
        sender: str,
        in_channel: bool,
        message: str,
        command: str,
    ):
        """Create message context object

        Args:
            bot (HalpyBOT): botclient/pseudoclient
            channel (str): channel message was sent in
            sender (str): user who sent the message
            in_channel (bool): True if in a channel, False if in DM
            message (str): message content

        """
        self.bot = bot
        self.channel = channel
        self.sender = sender
        self.in_channel = in_channel
        self.message = message
        self.command = command

    async def reply(self, message: str):
        """Send a message to the channel a message was sent in

        If the command was invoked in a DM, the user will be replied to in DM.

        Args:
            message (str): The message to be sent

        """
        message = re.sub(r"\n+", "\n", message)
        message = message.strip()
        if message:
            await self.bot.reply(self.channel, self.sender, self.in_channel, message)

    async def redirect(self, message: str):
        """Send a message to the person a DM-only command was run by

        Args:
            message (str): The message to be sent

        """
        if self.in_channel:
            await self.bot.reply(
                self.channel, self.sender, self.in_channel, "Responding in DMs!"
            )
        message = re.sub(r"\n+", "\n", message)
        message = message.strip()
        if message:
            await self.bot.reply(self.channel, self.sender, False, message)
