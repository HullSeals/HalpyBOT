""""
HalpyBOT v1.2

puppet.py - Bot sock puppet

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List

from src.packages.checks.checks import require_dm, require_permission, DeniedMessage
from .. import Commands


@require_dm()
@require_permission(req_level="CYBER", message=DeniedMessage.GENERIC)
@Commands.command("say")
async def cmd_say(ctx, args: List[str]):
    """
    Make the bot say something

    Usage: !say [channel] [text]
    Aliases: n/a
    """
    await ctx.bot.message(str(args[0]), ' '.join(args[1:]))