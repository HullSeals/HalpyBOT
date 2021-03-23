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

class Context:

    def __init__(self, bot: pydle.Client, channel: str, sender: str, in_channel: bool, message: str):
        self.bot = bot
        self.channel = channel
        self.sender = sender
        self.in_channel = in_channel
        self.message = message

    async def reply(self, message: str):
        await self.bot.reply(self.channel, self.sender, self.in_channel, message)


class Commands:

    commandList = {}
    is_root: bool = False

    class CommandInstance:
        def __init__(self, function, main: bool, name: str):
            Commands.commandList[name] = (function, main)

    @classmethod
    def command(cls, *args):
        def decorator(function):
            for name in args:
                cls.register(name, function, True if name == args[0] else False)
            return function
        return decorator

    @classmethod
    def register(cls, name, function, main: bool):
        if name in cls.commandList.keys():
            raise CommandAlreadyExists
        Commands.commandList[name] = (function, main)

    @classmethod
    async def invoke(cls, Command, Context: Context, Arguments: List[str]):
        # noinspection PyBroadException
        try:
            return await Commands.commandList[Command][0](Context, Arguments)
        # We actually want this to catch everything
        except Exception as er:
            raise CommandException(str(er))

    @classmethod
    async def get_commands(cls, mains: bool = False):
        if mains is False:
            return list(Commands.commandList.keys())
        else:
            cmdlist = []
            for command in Commands.commandList:
                if Commands.commandList[command][1] is True:
                    cmdlist.append(str(command))
            return cmdlist


class CommandGroup:

    subcommandList = {}
    group_name: str = "Unknown Group Name"

    def add_group(self, *names):
        for name in names:
            Commands.register(name, self, True if name == names[0] else False)
        self.group_name = names[0]

    def command(self, *args):
        def decorator(function):
            for name in args:
                if name in self.subcommandList.keys():
                    raise CommandAlreadyExists
                self.subcommandList[name] = (function, True if name == args[0] else False)
            return function

        return decorator

    async def __call__(self, Context: Context, Arguments: List[str]):
        if len(Arguments) == 0:
            return await Context.reply(f"Available {str(self.group_name)}: "
                                       f"{', '.join(scmd for scmd in self.subcommandList.keys())}")
        subcommand = Arguments[0].lower()
        if subcommand in self.subcommandList.keys():
            args = Arguments[1:]
            await self.subcommandList[subcommand][0](Context, args)
        else:
            await Context.reply(f"Subcommand not found! Try {config['IRC']['commandPrefix']}"
                                f"{self.group_name} to see all the options")


async def invoke_from_message(bot: pydle.Client, channel: str, sender: str, message: str):
    if message.startswith(config['IRC']['commandPrefix']):
        parts = message[1:].split(" ")
        command = parts[0].lower()
        args = parts[1:]
        in_channel = (True if bot.is_channel(channel) else False)
        ctx = Context(bot, channel, sender, in_channel, ' '.join(args[0:]))
        if command in Commands.commandList:
            try:
                return await Commands.invoke(Command=command, Context=ctx, Arguments=args)
            except CommandException as er:
                await ctx.reply(f"Unable to execute command: {str(er)}")
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