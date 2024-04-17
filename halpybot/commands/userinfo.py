"""
userinfo.py - Seal whox lookup commands

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List
from sqlalchemy.engine import Engine
from halpybot.packages.command.commandhandler import get_help_text
from ..packages.seals import whois
from ..packages.command import Commands
from ..packages.checks import needs_permission, needs_database, Pup
from ..packages.models import Context, Seal


async def whois_fetch(engine: Engine, cmdr: str):
    """Fetch the details of the user requested by WHOIS"""
    try:
        seal: Seal = await whois(engine, cmdr)
    except (KeyError, ValueError):
        return "No registered user found by that name!"
    return (
        f"CMDR {seal.name} has a Seal ID of {seal.seal_id}, registered on {seal.reg_date}"
        f"{seal.dw2_history} {seal.format_cmdrs}and has been involved with {seal.case_num} rescues."
    )


@Commands.command("whois")
@needs_permission(Pup)
@needs_database
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
    return await ctx.redirect(await whois_fetch(ctx.bot.engine, cmdr))


@Commands.command("whoami")
@needs_permission(Pup)
@needs_database
async def cmd_whoami(ctx: Context, args: List[str]):
    """
    List user information of a given user

    Usage: !whoami
    Aliases: n/a
    """
    cmdr = ctx.sender
    return await ctx.redirect(await whois_fetch(ctx.bot.engine, cmdr))
