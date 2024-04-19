""""
puppet.py - Bot sock puppet

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List

from ..packages.checks import needs_permission, Cyberseal, in_direct_message
from ..packages.command import Commands, get_help_text
from ..packages.models import Context


@Commands.command("say")
@in_direct_message
@needs_permission(Cyberseal, message="No.")
async def cmd_say(ctx: Context, args: List[str]):
    """
    Make the bot say something

    Usage: !say [channel] [text]
    Aliases: n/a
    """
    if len(args) <= 1:  # Minimum Number of Args is 2.
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, "say"))
    await ctx.bot.message(str(args[0]), " ".join(args[1:]))
