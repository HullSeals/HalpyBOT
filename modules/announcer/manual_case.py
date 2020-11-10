from typing import List
from modules.util.checks import require_permission, DeniedMessage
import logging
from ..util.checks import require_channel

send_to = ["#Repair-Requests", "#Code-Black", "#seal-bob"]

@require_channel()
@require_permission("DRILLED", message=DeniedMessage.DRILLED)
async def manual_case(ctx, args: List[str]):
    message = f"xxxx MANCASE xxxx\n" \
              f"{' '.join(args)}\n" \
              f"xxxx NEWCASE xxxx"
    for ch in send_to:
        await ctx.bot.message(ch, message)
        logging.info(f"Manual case by {ctx.sender} in {ctx.channel}: {args}")
    cn_message = f"New Manual Case Available -- <@&744998165714829334>\n" \
                 f"{' '.join(args)}"
    await ctx.bot.message("#case-notify", cn_message)


@require_channel()
@require_permission("DRILLED", message=DeniedMessage.DRILLED)
async def manual_kingfisher(ctx, args: List[str]):
    message = f"xxxx MANKFCASE xxxx\n" \
              f"{' '.join(args)}\n" \
              f"xxxx NEWKFCASE xxxx"
    for ch in send_to:
        await ctx.bot.message(ch, message)
        logging.info(f"Manual kingfisher case by {ctx.sender} in {ctx.channel}: {args}")
    cn_message = f"New Manual KFCase Available -- <@&744998165714829334>\n" \
                 f"{' '.join(args)}"
    await ctx.bot.message("#case-notify", cn_message)
