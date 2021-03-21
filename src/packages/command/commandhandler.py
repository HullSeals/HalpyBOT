"""
HalpyBOT v1.3

commandhandler.py - Handle bot commands and facts

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List
import pydle

from ..database.facts import fact_index, facts
from ..configmanager import config

class CommandException(Exception):
    """
    Base exception for all commands
    """

class CommandHandlerError(CommandException):
    """
    Base exception for command errors
    """

class CommandAlreadyExists(CommandHandlerError):
    """
    Raised when a command is registered twice
    """


class Commands:

    commandList = {}

    @classmethod
    def command(cls, *args):
        def decorator(function):
            for name in args:
                if name in cls.commandList.keys():
                    raise CommandAlreadyExists
                cls.commandList[str(name)] = function
            return function
        return decorator

class Context:

    def __init__(self, bot: pydle.Client, channel: str, sender: str, in_channel: bool, message: str):
        self.bot = bot
        self.channel = channel
        self.sender = sender
        self.in_channel = in_channel
        self.message = message

    async def reply(self, message: str):
        await self.bot.reply(self.channel, self.sender, self.in_channel, message)


async def on_message(bot: pydle.Client, channel: str, sender: str, message: str):
    if message.startswith(config['IRC']['commandPrefix']):
        parts = message[1:].split(" ")
        command = parts[0].lower()
        args = parts[1:]
        in_channel = (True if bot.is_channel(channel) else False)
        ctx = Context(bot, channel, sender, in_channel, ' '.join(args[0:]))
        if command in Commands.commandList:
            return await Commands.commandList[command](ctx, args)
        elif command in fact_index:
            return await recite_fact(ctx, args, fact=str(command))
        else:
            return


async def recite_fact(ctx, args: List[str], fact: str):

    # Sanity check
    if fact not in facts:
        return await ctx.reply("Cannot find fact! contact a cyberseal")

    # Public and PM, 1 version
    if f"{fact}_no_args" not in facts:
        if len(args) == 0:
            return await ctx.reply(facts[str(fact)])
        else:
            return await ctx.reply(f"{' '.join(str(seal) for seal in args)}: {facts[str(fact)]}")

    # Public and PM, args and noargs
    if len(args) == 0:
        await ctx.reply(facts[f"{str(fact)}_no_args"])
    else:
        await ctx.reply(f"{' '.join(str(seal) for seal in args)}: {facts[str(fact)]}")