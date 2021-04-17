"""
HalpyBOT v1.4

fact.py - Fact module management commands

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List, Optional
import re

from ..packages.command import Commands, Facts
from ..packages.models import Context
from ..packages.facts import Fact, FactUpdateError
from ..packages.checks import require_dm, require_permission, DeniedMessage
from ..packages.database import NoDatabaseConnection

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

@Commands.command("addfact")
@require_permission(req_level="ADMIN", message="Please contact an admin "
                                               "if you think a fact needs to be added")
async def cmd_addfact(ctx: Context, args: List[str]):
    """
    Add a new fact to the database

    Usage: !addfact [name-lang] [text]
    Aliases: n/a
    """

    if not args or len(args) < 2:
        return await ctx.reply("Usage: !addfact [name-lang] [text]")

    # Get language
    if '-' in args[0]:
        lang = args[0].split('-')[1]
        name = args[0].split('-')[0]
    else:
        name, lang = args[0], 'en'

    if not re.match(re.compile(r"^[a-z]{2}$"), lang):
        return await ctx.reply("Cannot comply: Language code must be ISO-639-1 compliant.")

    # Check if not already a fact/command
    # TODO move this to the fact package as soon as we can avoid the circular import
    if name in Facts.list(lang=lang) or name in Commands.get_commands():
        return await ctx.reply("Cannot comply: Fact already an existing fact/command!")
    try:

        await Facts.add_fact(name, lang, ' '.join(args[1:]), ctx.sender)
        return await ctx.reply("Fact has been added.")

    except NoDatabaseConnection:
        return await ctx.reply("Unable to add fact: please confirm that the bot is not "
                               "in offline mode.")
    except FactUpdateError:
        return await ctx.reply("Fact has been added, but cache could not be fully updated. "
                               "Please contact a cyberseal")

    # Raised when we don't have an English fact for this factname
    except ValueError:
        return await ctx.reply("Cannot add a fact that does not have an English "
                               "version registered")
