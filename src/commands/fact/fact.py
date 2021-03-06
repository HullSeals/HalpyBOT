"""
HalpyBOT v1.2

fact.py - Fact module bot_management commands

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""


from src.packages.checks.checks import require_permission, DeniedMessage, require_dm
from src.packages.database.facts import update_fact_index, basic_facts, clear_facts, get_facts
from typing import List
import logging
from src.packages.database.facts import add_fact, remove_fact, get_offline_facts
from src.packages.database import NoDatabaseConnection
from .. import Commands

@require_dm()
@require_permission(req_level="PUP", message=DeniedMessage.PUP)
@Commands.command("allfacts")
async def cmd_allfacts(ctx, args: List[str]):
    """
    List all registered facts

    Usage: !allfacts
    Aliases: n/a
    """
    listallfacts = f"{', '.join(str(fact) for fact in basic_facts)}"
    await ctx.reply(listallfacts)

@require_permission(req_level="CYBER", message=DeniedMessage.CYBER)
@Commands.command("ufi", "fact_update")
async def cmd_manual_ufi(ctx, args: List[str]):
    """
    Manually update the fact cache and index

    Usage: !ufi
    Aliases: fact_update
    """
    logging.info(f"FACT INDEX UPDATE by {ctx.sender}")
    try:
        await ctx.reply("Updating...")
        await clear_facts()
        await get_facts()
        await update_fact_index()
        await ctx.reply("Done.")
    except NoDatabaseConnection:
        await ctx.reply("Cannot update fact cache, running in OFFLINE MODE. "
                        "Contact a cyberseal immediately!")
        # Fetch offline facts, just in case the cache was flushed
        await get_offline_facts()
        await update_fact_index()


@require_permission(req_level="ADMIN", message=DeniedMessage.ADMIN)
@Commands.command("addfact")
async def cmd_addfact(ctx, args: List[str]):
    """
    Add a new fact to the database

    Usage: !addfact [name] (--dm) [facttext]
    Aliases: n/a
    """
    factname = args[0]
    facttext = ' '.join(arg for arg in args[1:])
    try:
        await add_fact(ctx, factname, facttext)
    except NoDatabaseConnection:
        return await ctx.reply("Cannot delete fact: running in OFFLINE MODE! "
                               "Contact a cyberseal immediately.")


@require_permission(req_level="ADMIN", message=DeniedMessage.ADMIN)
@Commands.command("deletefact")
async def cmd_deletefact(ctx, args: List[str]):
    """
    Delete a fact from the database

    Usage: !deletefact [factname]
    Aliases: n/a
    """
    factname = args[0]
    try:
        await remove_fact(ctx, factname)
    except NoDatabaseConnection:
        await ctx.reply("Cannot delete fact: running in OFFLINE MODE! "
                        "Contact a cyberseal immediately.")
