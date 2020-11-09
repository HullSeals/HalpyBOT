import main
from ..util.checks import require_permission, DeniedMessage, require_dm
from .fact import update_fact_index, basic_facts, get_facts
from typing import List
import logging
from .fact import add_fact, remove_fact, clear_facts

@require_dm()
@require_permission(req_level="PUP", message=DeniedMessage.PUP)
async def allfacts(ctx, args: List[str]):
    listallfacts = f"{', '.join(str(fact) for fact in basic_facts)}"
    await ctx.reply(listallfacts)

@require_permission(req_level="CYBER", message=DeniedMessage.CYBER)
async def manual_ufi(ctx, args: List[str]):
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
async def addfact(ctx, args: List[str]):
    factname = args[0]
    if args[1] == "--dm":
        reqdm = True
        facttext = ' '.join(arg for arg in args[2:])
    else:
        reqdm = False
        facttext = ' '.join(arg for arg in args[1:])
    await add_fact(ctx.bot, factname, facttext, ctx.sender,
                   reqdm, ctx.channel, ctx.sender, ctx.in_channel)


@require_permission(req_level="ADMIN", message=DeniedMessage.ADMIN)
async def deletefact(ctx, args: List[str]):
    factname = args[0]
    await remove_fact(ctx.bot, factname, ctx.channel,
                      ctx.sender, ctx.in_channel)
