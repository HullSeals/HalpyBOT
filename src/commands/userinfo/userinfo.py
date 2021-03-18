"""
HalpyBOT v1.2.2

edsm.py - EDSM Interface commands

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List
from src.packages.database.userinfo import *
from .. import Commands
from src.packages.checks.checks import require_permission, DeniedMessage, require_dm


@require_dm()
@require_permission(req_level="PUP", message=DeniedMessage.PUP)
@Commands.command("whois")
async def cmd_whois(ctx, args: List[str]):
    """
    List user information of a given user

    Usage: !whois
    Aliases: n/a
    """
    cmdr = ' '.join(args[0:])  # TODO replace by ctx method
    # Input validation
    if not cmdr:
        return await ctx.reply("No arguments given! Please provide a CMDR name.")
    return await ctx.reply(await whois(cmdr))


@require_dm()
@require_permission(req_level="PUP", message=DeniedMessage.PUP)
@Commands.command("whoami")
async def cmd_whoami(ctx, args: List[str]):
    """
    List user information of a given user

    Usage: !whoami
    Aliases: n/a
    """
    cmdr = ctx.sender
    return await ctx.reply(await whois(cmdr))
