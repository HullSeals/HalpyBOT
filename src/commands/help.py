"""
HalpyBOT v1.5

help.py - get command list and command details when queried

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List
import json

from ..packages.command import Commands
from ..packages.models import Context

@Commands.command("help")
async def help(ctx: Context, args: List[str]):
    """
    Reply with a list of commands or with details on a given command

    Usage: !help [command]
    Aliases: n/a
    """
    with open("data/help/commands.json", "r") as jsonfile:
        jsonDict = json.load(jsonfile)

    if not args:
        # Return low detail list of commands
        helpString = ""
        for catagory, commandDict in jsonDict.items():
            helpString += catagory
            for command in commandDict:
                helpString += "\t"+command
            helpString += "\n"
        await ctx.reply(helpString)
    else:
        # A specific command has been queried
        for commandDict in jsonDict.values():
            for command, details in commandDict.items():
                if command.lower() == args[0].lower():
                    arguments = details["arguments"]
                    aliases = details["aliases"]
                    usage = details["use"]
                    commandHelp = f"{command} {arguments}\nAliases: {aliases}\n{usage}"
                    await ctx.reply(commandHelp)
                    break
        else:
            # No command with the given name was found
            await ctx.reply("The command {args[0]} could not be found in the list. Try running help without an argument to get the list of commands")