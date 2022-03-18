""""
HalpyBOT v1.5.2

puppet.py - Bot sock puppet

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List

from ..packages.checks import Require, Cyberseal
from ..packages.command import Commands, get_help_text
from ..packages.models import Context


@Commands.command("say")
@Require.direct_message()
@Require.permission(Cyberseal, message="No.")
async def cmd_say(ctx: Context, args: List[str]):
    """
    Make the bot say something

    Usage: !say [channel] [text]
    Aliases: n/a
    """
    if len(args) == 0 or len(args) == 1:  # Minimum Number of Args is 2.
        return await ctx.reply(get_help_text("say"))
    await ctx.bot.message(str(args[0]), " ".join(args[1:]))
