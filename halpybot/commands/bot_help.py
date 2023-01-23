"""
bot_help.py - get command list and command details when queried

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List
import git
from halpybot import __version__
from ..packages.command import Commands, get_help_text
from ..packages.models import Context


@Commands.command("help")
async def hbot_help(ctx: Context, args: List[str]):
    """
    Reply with a list of commands or with details on a given command

    Usage: !help [command]
    Aliases: n/a
    """
    if not args:
        # Return low detail list of commands
        help_string = ""
        for category, command_dict in ctx.bot.commandsfile.items():
            help_string += category + "\n"
            help_string += "        " + ", ".join(command_dict) + "\n"
        # Remove final line break
        help_string = help_string[:-1]
        return await ctx.redirect(help_string)
    # A specific command has been queried
    help_text = get_help_text(ctx.bot.commandsfile, " ".join(args))
    if help_text is not None:
        return await ctx.reply(help_text)
    for arg in args:
        help_text = get_help_text(ctx.bot.commandsfile, arg)

        if help_text is None:
            help_string = ""
            for category, command_dict in ctx.bot.commandsfile.items():
                if arg == category:
                    help_string += category + "\n"
                    help_string += "        " + ", ".join(command_dict) + "\n"
                # Remove final line break
                help_string = help_string[:-1]
                if len(help_string) != 0:
                    return await ctx.redirect(help_string)

            await ctx.reply(
                f"The command {arg} could not be found in the list. Try running help without an argument to get"
                f" the list of commands"
            )
        else:
            await ctx.reply(help_text)


@Commands.command("about")
async def cmd_about(ctx: Context, args: List[str]):
    """
    Reply with the details of the bot including acknowledgements

    Usage: !about
    Aliases: n/a
    """
    try:
        repo = git.Repo()
        sha = repo.head.object.hexsha
        sha = sha[0:7]
        sha = f", build {sha}"
    except git.InvalidGitRepositoryError:
        sha = ""
    return await ctx.redirect(
        f"HalpyBOT v{str(__version__)}{sha}\n"
        f"Developed by the Hull Seals, using Pydle\n"
        f"HalpyBOT repository: https://hullse.al/HalpyBOT\n"
        f"Developed by: Rik079, Rixxan, Feliksas, and StuntPhish\n"
        f"Pydle: https://github.com/Shizmob/pydle/\n"
        f"Many thanks to the Pydle Devs and TFRM Techrats for their assistance "
        f"in the development of HalpyBOT."
    )
