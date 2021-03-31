"""
HalpyBOT v1.3.1

commandhandler.py - Handle bot commands and facts

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from __future__ import annotations
from typing import List
import pydle

from ..database.facts import fact_index, recite_fact
from ..configmanager import config
from typing import Coroutine

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
    """Message context object"""

    def __init__(self, bot: pydle.Client, channel: str, sender: str, in_channel: bool, message: str):
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

    async def reply(self, message: str):
        """Send a message to the channel a message was sent in

        If the command was invoked in a DM, the user will be replied to in DM.

        Args:
            message (str): The message to be sent

        """
        await self.bot.reply(self.channel, self.sender, self.in_channel, message)


class CommandGroup:
    """Group of commands

    Group registered as CommandGroup._root will be loaded by client on startup

    """

    _grouplist = []
    _root: CommandGroup = None

    @classmethod
    def get_group(cls, name: str):
        """Get a command group by name

        Args:
            name (str): Name of the command group

        Returns:
            (`CommandGroup` or None): Command group object if found, else None

        """
        for group in cls._grouplist:
            if name.lower() == group.name:
                return group
        return None

    @classmethod
    async def invoke_from_message(cls, bot: pydle.Client, channel: str, sender: str, message: str):
        """Invoke a command from a message

        For example, `message="!delaycase 1 test"` will result in cmd_DelayCase being called,
        with arguments [1, "test"]

        Args:
            bot (`pydle.Client`): botclient/pseudoclient the command was called from
            channel (str): channel the message was sent in
            sender (str): user who invoked the command
            message (str): content of the message

        """
        if message.startswith(config['IRC']['commandPrefix']):
            parts = message[1:].split(" ")
            command = parts[0].lower()
            args = parts[1:]
            in_channel = (True if bot.is_channel(channel) else False)
            ctx = Context(bot, channel, sender, in_channel, ' '.join(args[0:]))
            if command in Commands._commandList:
                try:
                    return await cls._root(Command=command, Context=ctx, Arguments=args)
                except CommandException as er:
                    await ctx.reply(f"Unable to execute command: {str(er)}")
            elif command in fact_index:
                return await recite_fact(ctx, args, fact=str(command))
            else:
                return

    @property
    def commandList(self):
        """dict: list of commands in this group"""
        return self._commandList

    @property
    def name(self):
        """str: name of the command group"""
        return self._group_name

    def __init__(self, is_root: bool = False):
        """Create new command group

        Args:
            is_root (bool): `True` if root group. This may only be initialized once

        Raises:
            CommandHandlerError: When two or more root groups are registered

        """
        self._is_root = is_root
        self._group_name = ""
        self._commandList = {}
        if CommandGroup._root is not None and is_root is True:
            raise CommandHandlerError("Can only have one root group")
        if is_root is True:
            CommandGroup._root = self
            self._group_name = "<ROOT>"
        CommandGroup._grouplist.append(self)

    def add_group(self, *names):
        """Attach group to root

        Do not attach root to itself or to another group, this will raise an error

        Args:
            *names: Name(s) of the group

        Raises:
            CommandHandlerError: Raised when root is registered to a group or to itself

        Todo:
            * Create command categories that are in the root group but tagged separately

        """
        if self._is_root:
            raise CommandHandlerError("Can not add root group to any other group")
        for name in names:
            CommandGroup._root._register(name, self, True if name == names[0] else False)
        self._group_name = names[0]

    def command(self, *names):
        """An IRC command

        Can be invoked from IRC by using the command prefix and command name.
        Make sure to import any file this is used in so it gets registered properly

        Args:
            *names: Command names

        Notes:
            This decorator must ALWAYS be the first decorator used on a command.
            Failure to comply with this guideline might result in authorization checks
            not working properly (security issue!) revoked fish privileges, and most importantly,
            being chased by Rik with a cleaver

        """
        def decorator(function):
            for name in names:
                self._register(name, function, True if name == names[0] else False)
            return function
        return decorator

    def _register(self, name, function, main: bool):
        """Register a command instance

        You need to use this for every name a command has.
        Do NOT use this method directly; use the @group.command decorator instead.

        Args:
            name (str): Command name
            function (Coroutine or CommandGroup): The function or group
                we want to call with the command
            main (bool): `True` if main name of the command, else `False

        Raises:
            CommandAlreadyExists: When attempting to register an already existing command


        """
        if name in self._commandList.keys():
            raise CommandAlreadyExists
        self._commandList[name] = (function, main)

    async def __call__(self, Command: str, Context: Context, Arguments: List[str]):
        """Call a command

        If the command is part of a group attached to root, `Command` is the group, and
        `Arguments[0]` the name of the subcommand.

        Args:
            Command (str): name of the command or command group
            Context (Context): Message context object
            Arguments (list of str): list of command arguments

        Raises:
            CommandHandlerError: Raised when a command or subcommand is not found
                (this is Bad News™ and should NEVER happen in production)
            CommandException: Raised when the command could not be executed due to errors
                in the command execution itself.

        """
        Command = Command.lower()
        # Sanity check
        if Command not in self.commandList:
            raise CommandHandlerError("(sub)command not found.")
        Cmd = self.commandList[Command][0]
        if isinstance(Cmd, CommandGroup):
            subgroup = CommandGroup.get_group(name=Cmd._group_name)
            if len(Arguments) < 1:
                return await Context.reply(f"Subcommands of {config['IRC']['commandPrefix']}"
                                           f"{Cmd._group_name}: "
                                           f"{', '.join(sub for sub in await subgroup.get_commands(True))}")
            await Cmd(Command=Arguments[0],
                      Context=Context, Arguments=Arguments[1:])
        else:
            try:
                await Cmd(Context, Arguments)
            except Exception as er:
                raise CommandException(er)

    async def invoke(self, Command, Context: Context, Arguments: List[str]):
        """Call a command

        This is an alias for `group.__call__`
        """
        await self.__call__(Command, Context, Arguments)

    async def get_commands(self, mains: bool = False):
        """Get a list of registered commands in a group

        Args:
            mains (bool): `True` if we only want the main names

        Returns:
            (list): All registered command names (mains only if mains = True)

        """
        if mains is False:
            return list(self._commandList.keys())
        else:
            cmdlist = []
            for command in self._commandList:
                if self._commandList[command][1] is True:
                    cmdlist.append(str(command))
            return cmdlist


Commands = CommandGroup(is_root=True)
