"""
HalpyBOT v1.4

fact.py - Fact module management commands

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List, Optional

from ..packages.command import Commands, Facts
from ..packages.models import Context
from ..packages.facts import Fact
from ..packages.checks import require_dm, require_permission, DeniedMessage

@Commands.command("factinfo")
@require_permission(req_level="MODERATOR", message=DeniedMessage.MODERATOR)
@require_dm()
async def cmd_getfactdata(ctx: Context, args: List[str]):
    """
    Get information about a fact

    Usage: !factinfo [name] [lang]
    Aliases: n/a
    """
    if not args or len(args) != 2:
        return await ctx.reply("Usage: !factinfo [name] [lang]")
    name = args[0]
    lang = args[1]
    fact: Optional[Fact] = await Facts.get_fact_object(name, lang)
    if fact is None:
        return await ctx.reply("Fact not found.")
    else:
        langlist = await Facts.get_fact_languages(name)
        reply = f"Fact: {fact.name}\n" \
                f"Language: {fact.language}\n" \
                f"All langs: {', '.join(lan.upper() for lan in langlist)}\n" \
                f"ID: {fact.ID}\n" \
                f"Author: {fact.author}\n" \
                f"Text: {fact.raw_text}"
        return await ctx.reply(reply)