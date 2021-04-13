""""
HalpyBOT v1.4

puppet.py - Bot sock puppet

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List

from ..packages.checks import require_permission, DeniedMessage, require_dm
from ..packages.command import Commands
from ..packages.models import Context


@Commands.command("say")
@require_dm()
@require_permission(req_level="CYBER", message=DeniedMessage.GENERIC)
async def cmd_say(ctx: Context, args: List[str]):
    """
    Make the bot say something

    Usage: !say [channel] [text]
    Aliases: n/a
    """
    await ctx.bot.message(str(args[0]), ' '.join(args[1:]))
