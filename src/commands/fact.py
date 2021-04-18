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
from ..packages.facts import Fact, FactUpdateError, FactHandlerError
from ..packages.checks import Require, Moderator, Admin
from ..packages.database import NoDatabaseConnection
from ..packages.utils import language_codes

langcodes = language_codes()

@Commands.command("factinfo")
@Require.permission(Moderator)
@Require.DM()
async def cmd_getfactdata(ctx: Context, args: List[str]):
    """
    Get information about a fact

    Usage: !factinfo [name-lang]
    Aliases: n/a
    """
    if not args or len(args) != 1:
        return await ctx.reply("Usage: !factinfo [name-lang]")
    name = args[0].split('-')[0]
    lang = args[0].split('-')[1] if len(args[0].split('-')) == 2 else 'en'
    fact: Optional[Fact] = await Facts.get_fact_object(name, lang)
    if fact is None:
        return await ctx.reply("Fact not found.")
    else:
        langlist = await Facts.get_fact_languages(name)
        reply = f"Fact: {fact.name}\n" \
                f"Language: {langcodes[lang.lower()] +  f' ({fact.language})'}\n" \
                f"All langs: {', '.join(f'{langcodes[lan.lower()]} ({lan.upper()})' for lan in langlist)}\n" \
                f"ID: {fact.ID}\n" \
                f"Author: {fact.author}\n" \
                f"Text: {fact.raw_text}"
        return await ctx.reply(reply)

@Commands.command("addfact")
@Require.permission(Admin)
async def cmd_addfact(ctx: Context, args: List[str]):
    """
    Add a new fact to the database

    Usage: !addfact [name-lang] [text]
    Aliases: n/a
    """

    if not args or len(args) < 2:
        return await ctx.reply("Usage: !addfact [name-lang] [text]")
    lang = args[0].split('-')[1] if len(args[0].split('-')) == 2 else 'en'
    name = args[0].split('-')[0]

    if lang not in langcodes:
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

@Commands.command("deletefact")
@Require.permission(Admin)
async def cmd_deletefact(ctx: Context, args: List[str]):
    """
    Delete a fact.

    Usage: !deletefact [fact-lang]
    Aliases: n/a
    """
    if not args or len(args) != 1:
        return await ctx.reply("Usage: !deletefact [fact-lang]")

    name = args[0].split('-')[0]
    lang = args[0].split('-')[1] if len(args[0].split('-')) == 2 else 'en'

    if await Facts.get_fact_object(name, lang) is None:
        return await ctx.reply("That fact does not exist.")

    try:
        await Facts.delete_fact(name, lang)
        return await ctx.reply("Fact has been deleted.")
    except NoDatabaseConnection:
        return await ctx.reply("Cannot comply: please confirm that the bot "
                               "is not in offline mode.")
    except FactHandlerError:
        return await ctx.reply("Cannot comply: All facts must have an English "
                               "version, please delete the version in other languages "
                               "first.")

@Commands.command("allfacts", "factlist", "listfacts")
@Require.DM()
async def cmd_listfacts(ctx: Context, args: List[str]):
    """
    Get a list off all facts in a language (English by default)

    Usage: !allfacts <language>
    Aliases: allfacts, listfacts
    """
    if not args:
        lang = 'en'
    else:
        lang = args[0]

    # Input validation
    if lang not in Facts.langcodes:
        return await ctx.reply("Cannot comply: Please specify a valid language code.")

    factlist = Facts.list(lang)

    if len(factlist) == 0:
        return await ctx.reply(f"No {langcodes[lang.lower()]} facts found.")
    else:
        return await ctx.reply(f"All {langcodes[lang.lower()]} facts:\n"
                               f"{', '.join(fact for fact in factlist)}")
