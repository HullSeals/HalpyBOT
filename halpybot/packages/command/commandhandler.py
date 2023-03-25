"""
commandhandler.py - Handle bot commands and facts

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from __future__ import annotations
from typing import List, TYPE_CHECKING, Dict, Optional, Tuple, Callable
from loguru import logger
from halpybot import config
from ..exceptions import CommandHandlerError, CommandAlreadyExists
from ..models import Context, HelpArguments

if TYPE_CHECKING:
    from ..ircclient import HalpyBOT


class CommandGroup:
    """Group of commands

    Group registered as CommandGroup._root will be loaded by client on startup

    """

    _grouplist: List[CommandGroup] = []
    _root: Optional[CommandGroup] = None

    def __init__(self, is_root: bool = False):
        """Create new command group

        Args:
            is_root (bool): `True` if root group. This may only be initialized once

        Raises:
            CommandHandlerError: When two or more root groups are registered

        """
        self._is_root = is_root
        self._group_name = ""
        self._command_list: Dict[str, Tuple[Callable, bool]] = {}
        self._fact_handler = None
        # Don't allow registration of multiple root groups
        if CommandGroup._root and is_root:
            raise CommandHandlerError("Can only have one root group")
        if is_root:
            CommandGroup._root = self
            self._group_name = "<ROOT>"
        CommandGroup._grouplist.append(self)

    @property
    def facthandler(self):
        """Fact handler object"""
        return self._fact_handler

    @facthandler.setter
    def facthandler(self, handler):
        self._fact_handler = handler

    @classmethod
    def get_group(cls, name: str):
        """Get a command group by name

        Args:
            name (str): Name of the command group

        Returns:
            (`CommandGroup` or None): Command group object if found, else None

        """
        for group in cls._grouplist:
            if name.casefold() == group.name:
                return group
        return None

    @property
    def command_list(self):
        """dict: list of commands in this group"""
        return self._command_list

    @property
    def name(self):
        """str: name of the command group"""
        return self._group_name

    async def invoke_from_message(
        self, bot: HalpyBOT, channel: str, sender: str, message: str
    ):
        """Invoke a command or fact from a message

        For example, `message="!delaycase 1 test"` will result in cmd_DelayCase being called,
        with arguments [1, "test"]

        Args:
            bot (HalpyBOT): botclient/pseudoclient the command was called from
            channel (str): channel the message was sent in
            sender (str): user who invoked the command
            message (str): content of the message

        """
        if not message.startswith(config.irc.command_prefix):
            return

        # Start off with assigning all variables we need
        parts = message[1:].split(" ")
        command = parts[0].casefold()
        args = [arg for arg in parts[1:] if arg]
        in_channel = bot.is_channel(channel)
        ctx = Context(bot, channel, sender, in_channel, " ".join(args[0:]), command)
        # Determines the language of an eventual fact
        lang = command.split("-")[1] if "-" in command else "en"

        # See if it's a command, and execute
        if command in bot.commandhandler.command_list:
            return await self.invoke_command(
                command=command, command_context=ctx, arguments=args
            )

        # Possible fact
        # Ignore if we have no fact handler attached
        if not self._fact_handler:
            return

        fact_name = command.split("-")[0]
        if fact_name in await self._fact_handler.get_fact_names():
            # Check for Language
            if lang not in await self._fact_handler.lang_by_fact(fact_name):
                lang = "en"
            return await ctx.reply(
                await self._fact_handler.fact_formatted(
                    fact=(fact_name, lang), arguments=args
                )
            )

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
            CommandGroup._root._register(name, self, bool(name == names[0]))
        # Set main name
        self._group_name = names[0]

    def command(self, *names):
        """An IRC command

        Can be invoked from IRC by using the command prefix and command name.
        Make sure to import any file this is used in, so it gets registered properly

        Args:
            *names: Command names

        Notes:
            This decorator must ALWAYS be the first decorator used on a command.
            Failure to comply with this guideline might result in authorization checks
            not working properly (security issue!) revoked fish privileges, and most importantly,
            being chased by Rik with a cleaver

        """

        def decorator(function):
            """Register every provided name"""
            for name in names:
                self._register(name, function, bool(name == names[0]))
            # Set command attribute, so we can check if a function is an IRC-facing command or not
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
        if name in self._command_list:
            raise CommandAlreadyExists
        self._command_list[name] = (function, main)

    async def invoke_command(
        self, command: str, command_context: Context, arguments: List[str]
    ):
        """Call a command

        If the command is part of a group attached to root, `Command` is the group, and
        `Arguments[0]` the name of the subcommand.

        Args:
            command (str): name of the command or command group
            command_context (Context): Message context object
            arguments (list of str): list of command arguments

        Raises:
            CommandHandlerError: Raised when a command or subcommand is not found
                (this is Bad News™ and should NEVER happen in production)
            CommandException: Raised when the command could not be executed due to errors
                in the command execution itself.

        """
        cmd = self.command_list.get(command.casefold())
        if cmd is None:
            raise CommandHandlerError(f"Command not found: {command}")
        cmd = cmd[0]
        if isinstance(cmd, CommandGroup):  # Command group
            subgroup = CommandGroup.get_group(name=cmd.name)
            # If no subcommand is provided, send a provisional help response
            if len(arguments) < 1:
                return await command_context.reply(
                    f"Subcommands of {config.irc.command_prefix}"
                    f"{cmd.name}: "
                    f"{', '.join(sub for sub in subgroup.get_commands(True))}"
                )
            # Recursion, yay!
            await cmd.invoke_command(
                command=arguments[0],
                command_context=command_context,
                arguments=arguments[1:],
            )
        else:
            try:
                await cmd(command_context, arguments)
            except Exception as cmd_ex:
                error_type: dict = {
                    AttributeError: "Walrus",
                    IndexError: "Leopard",
                    KeyError: "Bearded",
                    NameError: "Harbor",
                    SyntaxError: "Caspian",
                    TypeError: "Spotted",
                    ValueError: "Ringed",
                }
                set_error = (
                    error_type[type(cmd_ex)] if type(cmd_ex) in error_type else "Harp"
                )
                logger.exception(f"Failed to invoke command. Code: {set_error}")
                return await command_context.reply(
                    f"Unable to execute command. Error code: {set_error}"
                )

    def get_commands(self, mains: bool = False):
        """Get a list of registered commands in a group

        Args:
            mains (bool): `True` if we only want the main names

        Returns:
            (list): All registered command names (mains only if mains = True)

        """
        if not mains:
            return list(self._command_list.keys())
        return [str(cmd) for cmd, func in self._command_list.items() if func[1]]


def get_help_text(
    commandsfile: Dict[str, Dict[str, HelpArguments]], search_command: str
):
    """
    Retrieve the help text for usage and arguments of a command.

    Args:
        commandsfile (json object): The commandsfile from Context
        search_command (str): The command being looked up in the dictionary

    Returns:
        (str or None): Help instructions for a given command, None if unsuccessful.
    """
    search_command = search_command.casefold()
    for command_dict in commandsfile.values():
        for command, details in command_dict.items():
            command = command.casefold()
            if command == search_command or (
                "aliases" in details and search_command in details["aliases"]
            ):
                arguments = details["arguments"]
                aliases = details.get("aliases")
                aliases = f"\nAliases: {', '.join(aliases)}" if aliases else ""
                usage = details["use"]
                return (
                    f"Use: {config.irc.command_prefix}{command} {arguments} {aliases}\n"
                    f"{usage}"
                )
    return None


Commands = CommandGroup(is_root=True)
