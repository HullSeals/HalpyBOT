"""
HalpyBOT v1.4

userinfo.py - Seal whox lookup commands

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List

from ...packages.database.userinfo import *
from .. import Commands
from ...packages.checks import *
from ...packages.models import Context


@Commands.command("whois")
@require_dm()
@require_permission(req_level="PUP", message=DeniedMessage.PUP)
async def cmd_whois(ctx: Context, args: List[str]):
    """
    List user information of a given user

    Usage: !whois [user]
    Aliases: n/a
    """
    cmdr = ' '.join(args[0:])  # TODO replace by ctx method
    # Input validation
    if not cmdr:
        return await ctx.reply("No arguments given! Please provide a CMDR name.")
    return await ctx.reply(await whois(cmdr))


@Commands.command("whoami")
@require_dm()
@require_permission(req_level="PUP", message=DeniedMessage.PUP)
async def cmd_whoami(ctx: Context, args: List[str]):
    """
    List user information of a given user

    Usage: !whoami
    Aliases: n/a
    """
    cmdr = ctx.sender
    return await ctx.reply(await whois(cmdr))
