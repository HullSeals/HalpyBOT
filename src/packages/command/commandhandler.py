"""
HalpyBOT v1.3

commandhandler.py - Handle bot commands and facts

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
from __future__ import annotations
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


class CommandGroup:

    grouplist = []
    root: CommandGroup = None

    @classmethod
    def get_group(cls, name: str):
        for group in cls.grouplist:
            if name.lower() == group.group_name:
                return group
        return None

    @classmethod
    async def invoke_from_message(cls, bot: pydle.Client, channel: str, sender: str, message: str):
        if message.startswith(config['IRC']['commandPrefix']):
            parts = message[1:].split(" ")
            command = parts[0].lower()
            args = parts[1:]
            in_channel = (True if bot.is_channel(channel) else False)
            ctx = Context(bot, channel, sender, in_channel, ' '.join(args[0:]))
            if command in Commands.commandList:
                try:
                    return await cls.root(Command=command, Context=ctx, Arguments=args)
                except CommandException as er:
                    await ctx.reply(f"Unable to execute command: {str(er)}")
            elif command in fact_index:
                return await recite_fact(ctx, args, fact=str(command))
            else:
                return

    def __init__(self, is_root: bool = False):
        self.is_root = is_root
        self.group_name = ""
        self.commandList = {}
        if CommandGroup.root is not None and is_root is True:
            raise CommandHandlerError("Can only have one root group")
        if is_root is True:
            CommandGroup.root = self
            self.group_name = "<ROOT>"
        CommandGroup.grouplist.append(self)

    def add_group(self, *names):
        if self.is_root:
            raise CommandHandlerError("Can not add root group to any other group")
        for name in names:
            CommandGroup.root.register(name, self, True if name == names[0] else False)
        self.group_name = names[0]

    def command(self, *names):
        def decorator(function):
            for name in names:
                self.register(name, function, True if name == names[0] else False)
            return function
        return decorator

    def register(self, name, function, main: bool):
        if name in self.commandList.keys():
            raise CommandAlreadyExists
        self.commandList[name] = (function, main)

    async def __call__(self, Command: str, Context: Context, Arguments: List[str]):
        Command = Command.lower()
        # Sanity check
        if Command not in self.commandList:
            raise CommandHandlerError("(sub)command not found.")
        Cmd = self.commandList[Command][0]
        if isinstance(Cmd, CommandGroup):
            subgroup = CommandGroup.get_group(name=Cmd.group_name)
            if len(Arguments) < 1:
                return await Context.reply(f"Subcommands of {config['IRC']['commandPrefix']}"
                                           f"{Cmd.group_name}: "
                                           f"{', '.join(sub for sub in await subgroup.get_commands(True))}")
            await Cmd(Command=Arguments[0],
                      Context=Context, Arguments=Arguments[1:])
        else:
            try:
                await Cmd(Context, Arguments)
            except Exception as er:
                raise CommandException(er)

    async def invoke(self, Command, Context: Context, Arguments: List[str]):
        # This is just an alias for __call__:
        await self.__call__(Command, Context, Arguments)

    async def get_commands(self, mains: bool = False):
        if mains is False:
            return list(self.commandList.keys())
        else:
            cmdlist = []
            for command in self.commandList:
                if self.commandList[command][1] is True:
                    cmdlist.append(str(command))
            return cmdlist


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

Commands = CommandGroup(is_root=True)
