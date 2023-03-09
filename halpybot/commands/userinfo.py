"""
userinfo.py - Seal whox lookup commands

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List

from halpybot.packages.command.commandhandler import get_help_text

from ..packages.seals import whois
from ..packages.command import Commands
from ..packages.checks import Require, Pup
from ..packages.models import Context, Seal


@Commands.command("whois")
@Require.permission(Pup)
@Require.database()
async def cmd_whois(ctx: Context, args: List[str]):
    """
    List user information of a given user

    Usage: !whois [user]
    Aliases: n/a
    """
    if len(args) == 0:
        return await ctx.redirect(get_help_text(ctx.bot.commandsfile, "whois"))
    cmdr = args[0]
    if cmdr.casefold() == "halpybot":
        return await ctx.redirect(
            "That's me! CMDR HalpyBOT has a Seal ID of 0, registered 14.8 billion years ago, "
            "is a DW2 Veteran and Founder Seal with registered CMDRs of Arf! Arf! Arf!, "
            "and has been involved with countless rescues."
        )
    try:
        seal: Seal = await whois(ctx.bot.engine, cmdr)
    except (KeyError, ValueError):
        return await ctx.redirect("No registered user found by that name!")
    return await ctx.redirect(
        f"CMDR {seal.name} has a Seal ID of {seal.seal_id}, registered on {seal.reg_date}{seal.dw2_history}"
        f" {seal.cmdrs}, and has been involved with {seal.case_num} rescues."
    )


@Commands.command("whoami")
@Require.permission(Pup)
@Require.database()
async def cmd_whoami(ctx: Context, args: List[str]):
    """
    List user information of a given user

    Usage: !whoami
    Aliases: n/a
    """
    cmdr = ctx.sender
    try:
        seal: Seal = await whois(ctx.bot.engine, cmdr)
    except (KeyError, ValueError):
        return await ctx.redirect("No registered user found by that name!")
    return await ctx.redirect(
        f"CMDR {seal.name} has a Seal ID of {seal.seal_id}, registered on {seal.reg_date}{seal.dw2_history}"
        f" {seal.cmdrs}, and has been involved with {seal.case_num} rescues."
    )
