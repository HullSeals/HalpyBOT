"""
HalpyBOT v1.3.1

manual_case.py - Manual case creation module

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List
import logging
import requests

from ...packages.checks import *
from .. import Commands
from ...packages.configmanager import config

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
    for ch in config['Announcer.cases']['channels'].split(", "):
        await ctx.bot.message(ch, message)
        logging.info(f"Manual case by {ctx.sender} in {ctx.channel}: {args}")
    cn_message = {
        "content": f"New Manual Case -- " + config['Discord Notifications']['CaseNotify'] + "\n"
                   f"{' '.join(args)}",
        "username": "HalpyBOT"
    }
    url = config['Discord Notifications']['URL']
    try:
        requests.post(url, json=cn_message)
    except requests.exceptions.HTTPError as err:
        logging.error(err)

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
    for ch in config['Announcer.cases']['channels'].split(", "):
        await ctx.bot.message(ch, message)
        logging.info(f"Manual kingfisher case by {ctx.sender} in {ctx.channel}: {args}")
    cn_message = {
        "content": f"New Manual Kingfisher Case -- " + config['Discord Notifications']['CaseNotify'] + "\n"
                   f"{' '.join(args)}",
        "username": "HalpyBOT"
    }
    url = config['Discord Notifications']['URL']
    try:
        requests.post(url, json=cn_message)
    except requests.exceptions.HTTPError as err:
        logging.error(err)


@Commands.command("tsping")
@require_channel()
@require_permission("DRILLED", message=DeniedMessage.DRILLED)
async def cmd_trained_ping(ctx, args: List[str]):
    """
    Alert the "Trained Seals" role in Discord that CMDRs
    are needed for this case. Annoying AF and not to be used lightly.

    Usage: !tsping
    Aliases: none
    """
    logging.info(f"Manual kingfisher case by {ctx.sender} in {ctx.channel}: {args}")
    cn_message = {
        "content": f"Attention to the Above Case, Seals! -- " + config['Discord Notifications']['TrainedRole'] + "\n"
                   f"Message triggered by {ctx.sender}",
        "username": "HalpyBOT"
    }
    url = config['Discord Notifications']['URL']
    try:
        requests.post(url, json=cn_message)
    except requests.exceptions.HTTPError as err:
        logging.error(err)
    await ctx.reply("Notification Sent!")
