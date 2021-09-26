"""
HalpyBOT v1.5

commandhandler.py - Handle bot commands and facts

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from __future__ import annotations
from typing import List
import pydle

from src import __version__
from ..configmanager import config
from ..models import Context


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


class CommandGroup:
    """Group of commands

    Group registered as CommandGroup._root will be loaded by client on startup

    """

    _grouplist = []
    _root: CommandGroup = None

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
        self._factHandler = None
        # Don't allow registration of multiple root groups
        if CommandGroup._root is not None and is_root is True:
            raise CommandHandlerError("Can only have one root group")
        if is_root is True:
            CommandGroup._root = self
            self._group_name = "<ROOT>"
        CommandGroup._grouplist.append(self)

    @property
    def facthandler(self):
        """Fact handler object"""
        return self._factHandler

    @facthandler.setter
    def facthandler(self, handler):
        self._factHandler = handler

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

    @property
    def commandList(self):
        """dict: list of commands in this group"""
        return self._commandList

    @property
    def name(self):
        """str: name of the command group"""
        return self._group_name

    async def invoke_from_message(self, bot: pydle.Client, channel: str, sender: str, message: str):
        """Invoke a command or fact from a message

        For example, `message="!delaycase 1 test"` will result in cmd_DelayCase being called,
        with arguments [1, "test"]

        Args:
            bot (`pydle.Client`): botclient/pseudoclient the command was called from
            channel (str): channel the message was sent in
            sender (str): user who invoked the command
            message (str): content of the message

        """
        if message.startswith(config['IRC']['commandPrefix']):
            # Start off with assigning all variables we need
            parts = message[1:].split(" ")
            command = parts[0].lower()
            args = parts[1:]
            in_channel = bot.is_channel(channel)
            ctx = Context(bot, channel, sender, in_channel, ' '.join(args[0:]))
            # Determines the language of an eventual fact
            lang = command.split('-')[1] if '-' in command else 'en'

            # See if it's a command, and execute
            if command in Commands._commandList:
                try:
                    return await self.invoke_command(Command=command, Context=ctx, Arguments=args)
                except CommandException as er:
                    await ctx.reply(f"Unable to execute command: {str(er)}")

            # Possible fact

            # Ignore if we have no fact handler attached
            if not self._factHandler:
                return

            # Are we requesting a specific language?
            elif command.split('-')[0] in await self._factHandler.get_fact_names():
                factname = command.split('-')[0]

                # Do we have a fact for this language?
                if lang not in list(await self._factHandler.lang_by_fact(factname)):
                    lang = 'en'

                return await ctx.reply(await self._factHandler.fact_formatted(fact=(command.split('-')[0], lang),
                                                                              arguments=args))

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
        # Set main name
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
            # Register every provided name
            for name in names:
                self._register(name, function, True if name == names[0] else False)
            # Set command attribute so we can check if a function is an IRC-facing command or not
            setattr(function, "is_command", True)
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

    async def invoke_command(self, Command: str, Context: Context, Arguments: List[str]):
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
        if isinstance(Cmd, CommandGroup):  # Command group
            subgroup = CommandGroup.get_group(name=Cmd._group_name)
            # If no subcommand is provided, send a provisional help response
            if len(Arguments) < 1:
                return await Context.reply(f"Subcommands of {config['IRC']['commandPrefix']}"
                                           f"{Cmd._group_name}: "
                                           f"{', '.join(sub for sub in subgroup.get_commands(True))}")
            # Recursion, yay!
            await Cmd.invoke_command(Command=Arguments[0],
                                     Context=Context, Arguments=Arguments[1:])
        else:
            try:
                await Cmd(Context, Arguments)
            except Exception as er:
                raise CommandException(er)

    def get_commands(self, mains: bool = False):
        """Get a list of registered commands in a group

        Args:
            mains (bool): `True` if we only want the main names

        Returns:
            (list): All registered command names (mains only if mains = True)

        """
        if mains is False:
            return list(self._commandList.keys())
        else:
            return [str(cmd) for cmd in self._commandList if self._commandList[cmd][1] is True]


Commands = CommandGroup(is_root=True)

@Commands.command("about")
async def cmd_about(ctx: Context, args: List[str]):
    return await ctx.reply(f"HalpyBOT v{str(__version__)}\n"
                           f"Developed by the Hull Seals, using Pydle\n"
                           f"HalpyBOT repository: https://gitlab.com/hull-seals/code/irc/halpybot\n"
                           f"Developed by: Rik079, Rixxan, Feliksas\n"
                           f"Pydle: https://github.com/Shizmob/pydle/\n"
                           f"Many thanks to the Pydle Devs and TFRM Techrats for their assistance "
                           f"in the development of HalpyBOT.")
