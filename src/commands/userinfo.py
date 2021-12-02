"""
HalpyBOT v1.5

userinfo.py - Seal whox lookup commands

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List

from ..packages.seals import whois
from ..packages.command import Commands
from ..packages.checks import Require, Pup
from ..packages.models import Context


@Commands.command("whois")
@Require.DM()
@Require.permission(Pup)
async def cmd_whois(ctx: Context, args: List[str]):
    """
    List user information of a given user

    Usage: !whois [user]
    Aliases: n/a
    """
    if len(args) == 0:
        return await ctx.reply("!whois [user]: Returns information about a given user.")
    cmdr = ' '.join(args[0:])  # TODO replace by ctx method
    if cmdr.lower() in ("halpybot"):
        return await ctx.reply("That's me! CMDR HalpyBOT has a Seal ID of 0, "
                               "registered 14.8 billion years ago, is a DW2 Veteran and Founder Seal "
                               "with registered CMDRs of Arf! Arf! Arf!, and has been involved with countless rescues.")

    return await ctx.reply(await whois(cmdr))


@Commands.command("whoami")
@Require.DM()
@Require.permission(Pup)
async def cmd_whoami(ctx: Context, args: List[str]):
    """
    List user information of a given user

    Usage: !whoami
    Aliases: n/a
    """
    cmdr = ctx.sender
    return await ctx.reply(await whois(cmdr))
