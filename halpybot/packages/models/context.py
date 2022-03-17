"""
HalpyBOT v1.5.2

context.py - Message context object

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import pydle


class Context:
    """Message context object"""

    def __init__(self, bot: pydle.Client, channel: str, sender: str, in_channel: bool, message: str,
                 command: str):
        """Create message context object

        Args:
            bot (`pydle.Client`): botclient/pseudoclient
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
        await self.bot.reply(self.channel, self.sender, self.in_channel, message)

    async def redirect(self, message: str):
        """Send a message to the person a DM-only command was run by

        Args:
            message (str): The message to be sent

        """
        if self.in_channel is True:
            await self.bot.reply(self.channel, self.sender, self.in_channel, "Responding in DMs!")
        await self.bot.reply(self.channel, self.sender, False, message)
