"""
HalpyBOT v1.2.3

manual_case.py - Manual case creation module

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List
import logging

from ...packages.checks import *
from .. import Commands

send_to = ["#Repair-Requests", "#seal-bob"]

@Commands.command("manualcase", "mancase")
@require_channel()
@require_permission("DRILLED", message=DeniedMessage.DRILLED)
async def cmd_manual_case(ctx, args: List[str]):
    """
    Create a manual case

    Usage: !manualcase [case info]
    Aliases: mancase
    """
    message = f"xxxx MANCASE -- NEWCASE xxxx\n" \
              f"{' '.join(args)}\n" \
              f"xxxxxxxx"
    for ch in send_to:
        await ctx.bot.message(ch, message)
        logging.info(f"Manual case by {ctx.sender} in {ctx.channel}: {args}")
    cn_message = f"New Manual Case Available -- <@&744998165714829334>\n" \
                 f"{' '.join(args)}"
    await ctx.bot.message("#case-notify", cn_message)


@Commands.command("manualfish", "manfish")
@require_channel()
@require_permission("DRILLED", message=DeniedMessage.DRILLED)
async def cmd_manual_kingfisher(ctx, args: List[str]):
    """
    Create a manual kingfisher case

    Usage: !manualfish [case info]
    Aliases: manfish
    """
    message = f"xxxx MANKFCASE -- NEWCASE xxxx\n" \
              f"{' '.join(args)}\n" \
              f"xxxxxxxx"
    for ch in send_to:
        await ctx.bot.message(ch, message)
        logging.info(f"Manual kingfisher case by {ctx.sender} in {ctx.channel}: {args}")
    cn_message = f"New Manual KFCase Available -- <@&744998165714829334>\n" \
                 f"{' '.join(args)}"
    await ctx.bot.message("#case-notify", cn_message)


@Commands.command("wssPing")
@require_channel()
@require_permission("DRILLED", message=DeniedMessage.DRILLED)
async def cmd_wss_ping(ctx, args: List[str]):
    """
    Alert the "Why So Sealious" role that CMDRs are needed for this case. Annoying AF and not to be used lightly.

    Usage: !wssPing
    Aliases: none
    """
    cn_message = f"Message from {ctx.sender}: Attention to the Above Cases, Seals! -- <@&591822215238909966>"
    await ctx.bot.message("#case-notify", cn_message)
    await ctx.reply("Notification Sent!")
