"""
fact.py - Fact module management commands

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List, Optional
from loguru import logger

from ..packages.command import Commands, get_help_text
from ..packages.models import Context
from ..packages.facts import (
    Fact,
    FactUpdateError,
    FactHandlerError,
    InvalidFactException,
    Facts,
)
from ..packages.checks import Require, Moderator, Admin, Cyberseal
from ..packages.database import NoDatabaseConnection
from ..packages.utils import language_codes, strip_non_ascii
from ..packages.configmanager import config


langcodes = language_codes()


@Commands.command("factinfo")
@Require.permission(Moderator)
async def cmd_getfactdata(ctx: Context, args: List[str]):
    """
    Get information about a fact

    Usage: !factinfo [name-lang]
    Aliases: n/a
    """
    if not args or len(args) != 1:
        return await ctx.reply(get_help_text("factinfo"))
    name = args[0].split("-")[0]
    lang = args[0].split("-")[1] if len(args[0].split("-")) == 2 else "en"
    fact: Optional[Fact] = await Facts.get(name, lang)
    if fact is None:
        return await ctx.redirect("Fact not found.")
    langlist = await Facts.lang_by_fact(name)
    reply = (
        f"Fact: {fact.name}\n"
        f"Language: {langcodes[lang.casefold()]} ({fact.language})\n"
        f"All langs: {', '.join(f'{langcodes[lan.casefold()]} ({lan.upper()})' for lan in langlist)}\n"
        f"ID: {fact.ID}\n"
        f"Author: {fact.author}\n"
        f"Text: {fact.raw_text}"
    )
    return await ctx.redirect(reply)


@Commands.command("addfact")
@Require.permission(Admin)
async def cmd_addfact(ctx: Context, args: List[str]):
    """
    Add a new fact to the database

    Usage: !addfact [name-lang] [text]
    Aliases: n/a
    """

    if not args or len(args) < 2:
        return await ctx.reply(get_help_text("addfact"))
    lang = args[0].split("-")[1] if len(args[0].split("-")) == 2 else "en"
    name = args[0].split("-")[0]

    if lang not in langcodes:
        return await ctx.reply(
            "Cannot comply: Language code must be ISO-639-1 compliant."
        )

    try:
        # Strip non-ASCII from facts, to ensure only standard ASCII are used.
        fact = " ".join(args[1:])
        fact = strip_non_ascii(fact)
        fact = str(fact[0])
        await Facts.add_fact(name, lang, fact, ctx.sender)
        return await ctx.reply("Fact has been added.")

    except NoDatabaseConnection:
        return await ctx.reply(
            "Unable to add fact: No database connection available. Entering Offline Mode, "
            "contact a cyberseal."
        )
    except FactUpdateError:
        logger.exception("Fact added, but cache not updated.")
        return await ctx.reply("An exception occured. Please contact a cyberseal!")

    # Raised when fact name is illegal for some reason
    except InvalidFactException:
        logger.exception("Cannot add fact!")
        return await ctx.reply("Error! Cannot add fact.")


@Commands.command("deletefact")
@Require.permission(Admin)
async def cmd_deletefact(ctx: Context, args: List[str]):
    """
    Delete a fact.

    Usage: !deletefact [fact-lang]
    Aliases: n/a
    """
    if not args or len(args) != 1:
        return await ctx.reply(get_help_text("deletefact"))

    name = args[0].split("-")[0]
    lang = args[0].split("-")[1] if len(args[0].split("-")) == 2 else "en"

    if await Facts.get(name, lang) is None:
        return await ctx.reply("That fact does not exist.")

    try:
        await Facts.delete_fact(name, lang)
        return await ctx.reply("Fact has been deleted.")
    except NoDatabaseConnection:
        logger.exception("Unable to add fact, database error!")
        return await ctx.reply(
            "Unable to add fact: No database connection available. Entering Offline Mode, "
            "contact a cyberseal."
        )
    except FactHandlerError:
        logger.exception("Fact Handling Error, probably no english variant.")
        return await ctx.reply(
            "Cannot comply: All facts must have an English "
            "version, please delete the version in other languages "
            "first."
        )


@Commands.command("allfacts", "factlist", "listfacts")
async def cmd_listfacts(ctx: Context, args: List[str]):
    """
    Get a list off all facts in a language (English by default)

    Usage: !allfacts <language>
    Aliases: allfacts, listfacts
    """
    if not args:
        lang = "en"
    else:
        lang = args[0].casefold()

    # Input validation
    if lang not in langcodes:
        return await ctx.redirect(
            "Cannot comply: Please specify a valid language code."
        )

    factlist = Facts.list(lang)

    if len(factlist) == 0:
        return await ctx.redirect(f"No {langcodes[lang.casefold()]} facts found.")
    return await ctx.redirect(
        f"All {langcodes[lang.casefold()]} facts:\n"
        f"{', '.join(fact for fact in factlist)}"
    )


@Commands.command("editfact", "updatefact")
@Require.permission(Admin)
async def cmd_editfact(ctx: Context, args: List[str]):
    """
    Edit a fact

    Usage: !editfact [name-lang] [new text]
    Aliases: updatefact
    """
    if not args or len(args) < 2:
        return await ctx.reply(get_help_text("editfact"))

    name = args[0].split("-")[0]
    lang = args[0].split("-")[1] if len(args[0].split("-")) == 2 else "en"

    fact = await Facts.get(name, lang)
    if fact is None:
        return await ctx.reply("That fact does not exist.")
    try:
        # Strip non-ASCII from facts, to ensure only standard ASCII are used.
        message = " ".join(args[1:])
        message = strip_non_ascii(message)
        message = str(message[0])
        fact.text = message
        return await ctx.reply("Fact successfully edited.")
    except NoDatabaseConnection:
        logger.exception("No database connection! Fact not edited. ")
        return await ctx.reply(
            "Unable to edit fact: No database connection available. Entering Offline Mode, "
            "contact a cyberseal."
        )
    except FactUpdateError:
        logger.exception("Fact does not exist on the database!")
        return await ctx.reply(
            "Unable to update a fact that only "
            "exists in local storage, please update "
            "the fact cache and try again."
        )


@Commands.command("ufi", "updatefactindex")
@Require.permission(Cyberseal)
async def cmd_ufi(ctx: Context, args: List[str]):
    """
    Manually update the fact cache.

    Usage: !ufi
    Aliases: updatefactindex
    """
    offline_start = config["Offline Mode"]["enabled"]
    if offline_start == "True":
        return await ctx.reply("Cannot update cache while in offline mode.")
    try:
        await Facts.fetch_facts(preserve_current=True)
    except NoDatabaseConnection:
        logger.exception("No Database Connection.")
        return await ctx.reply(
            "Cannot comply: No database connection. "
            "Preserving and locking current fact cache, "
            "update command ignored."
        )

    return await ctx.reply("Fact cache updated.")
