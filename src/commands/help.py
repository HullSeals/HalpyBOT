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

from ..packages.command import Commands, get_help_text
from ..packages.models import Context
from src import __version__

with open("data/help/commands.json", "r") as jsonfile:
    json_dict = json.load(jsonfile)


@Commands.command("help")
async def help(ctx: Context, args: List[str]):
    """
    Reply with a list of commands or with details on a given command

    Usage: !help [command]
    Aliases: n/a
    """

    if not args:
        # Return low detail list of commands
        help_string = ""
        for catagory, command_dict in json_dict.items():
            help_string += catagory + "\n"
            help_string += "        " + ", ".join(command_dict) + "\n"
        # Remove final line break
        help_string = help_string[:-1]
        await ctx.redirect(help_string)
    else:
        # A specific command has been queried
        help_text = get_help_text(args[0])

        if help_text == None:
            await ctx.redirect(
                f"The command {args[0]} could not be found in the list. Try running help without an argument to get "
                f"the list of commands")
        else:
            await ctx.reply(help_text)


@Commands.command("about")
async def cmd_about(ctx: Context, args: List[str]):
    return await ctx.redirect(f"HalpyBOT v{str(__version__)}\n"
                           f"Developed by the Hull Seals, using Pydle\n"
                           f"HalpyBOT repository: https://hullse.al/HalpyBOT\n"
                           f"Developed by: Rik079, Rixxan, Feliksas, and StuntPhish\n"
                           f"Pydle: https://github.com/Shizmob/pydle/\n"
                           f"Many thanks to the Pydle Devs and TFRM Techrats for their assistance "
                           f"in the development of HalpyBOT.")
