"""
HalpyBOT v1.5

fact_management.py - Fact module settings commands

Copyright (c) 2020 The Hull Seals,
All rights reserved

Licensed under the GNU General Public License
See license.md
"""


from ..util.checks import require_permission, DeniedMessage, require_dm
from .fact import update_fact_index, basic_facts, get_facts
from typing import List
import logging
from .fact import add_fact, remove_fact, clear_facts

@require_dm()
@require_permission(req_level="PUP", message=DeniedMessage.PUP)
async def cmd_allfacts(ctx, args: List[str]):
    """
    List all registered facts

    Usage: !allfacts
    Aliases: n/a
    """
    listallfacts = f"{', '.join(str(fact) for fact in basic_facts)}"
    await ctx.reply(listallfacts)

@require_permission(req_level="CYBER", message=DeniedMessage.CYBER)
async def cmd_manual_ufi(ctx, args: List[str]):
    """
    Manually update the fact cache and index

    Usage: !ufi
    Aliases: fact_update
    """
    logging.info(f"FACT INDEX UPDATE by {ctx.sender}")
    await ctx.reply("Defenestrating facts...")
    await ctx.reply("Clearing fact index...")
    await clear_facts()
    await ctx.reply("Fetching facts...")
    await get_facts()
    await ctx.reply("Updating...")
    await update_fact_index()
    await ctx.reply("Done.")


@require_permission(req_level="ADMIN", message=DeniedMessage.ADMIN)
async def cmd_addfact(ctx, args: List[str]):
    """
    Add a new fact to the database

    Usage: !addfact [name] <--dm> [facttext]
    Aliases: n/a
    """
    factname = args[0]
    if args[1] == "--dm":
        reqdm = True
        facttext = ' '.join(arg for arg in args[2:])
    else:
        reqdm = False
        facttext = ' '.join(arg for arg in args[1:])
    await add_fact(ctx, factname, facttext, reqdm)


@require_permission(req_level="ADMIN", message=DeniedMessage.ADMIN)
async def cmd_deletefact(ctx, args: List[str]):
    """
    Delete a fact from the database

    Usage: !deletefact [factname]
    Aliases: n/a
    """
    factname = args[0]
    await remove_fact(ctx, factname)
