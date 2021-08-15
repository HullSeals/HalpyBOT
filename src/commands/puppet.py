""""
HalpyBOT v1.5

puppet.py - Bot sock puppet

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List

from ..packages.checks import Require, Cyberseal
from ..packages.command import Commands
from ..packages.models import Context


@Commands.command("say")
@Require.DM()
@Require.permission(Cyberseal, message="No.")
async def cmd_say(ctx: Context, args: List[str]):
    """
    Make the bot say something

    Usage: !say [channel] [text]
    Aliases: n/a
    """
    await ctx.bot.message(str(args[0]), ' '.join(args[1:]))
