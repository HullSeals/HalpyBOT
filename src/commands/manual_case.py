"""
HalpyBOT v1.4

manual_case.py - Manual case creation module

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List
import logging
# We'll temporarily use Requests
import requests
import datetime

from ..packages.command import Commands
from ..packages.checks import Require, Drilled
from ..packages.models import Context
from ..packages.configmanager import config

@Commands.command("manualcase", "mancase", "manualfish", "manfish")
@Require.permission(Drilled)
@Require.channel()
async def cmd_manualCase(ctx: Context, args: List[str]):
    """
    Manually create a new case

    Usage: !manualcase [IRC name] [case info]
    Aliases: mancase, manualfish, manfish
    """
    info = ctx.message
    logging.info(f"Manual case by {ctx.sender} in {ctx.channel}")
    for channel in config["Manual Case"]["send_to"].split():
        await ctx.bot.message(channel, f"xxxx MANCASE -- NEWCASE xxxx\n"
                                       f"{info}\n"
                                       f"xxxxxxxx")

    # Send to Discord
    cn_message = {
        "content": f"New Incoming Case - {config['Discord Notifications']['CaseNotify']}",
        "username": "HalpyBOT",
        "avatar_url": "https://hullseals.space/images/emblem_mid.png",
        "tts": False,
        "embeds": [
            {
                "title": "New Manual Case!",
                "type": "rich",
                "timestamp": f"{datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')}",
                "color": 16093727,
                "footer": {
                    "text": f"{ctx.sender}",
                    "icon_url": "https://hullseals.space/images/emblem_mid.png",
                },
                "fields": [
                    {
                        "name": "IRC Name:",
                        "value": str(args[0]),
                        "inline": False
                    },

                    {
                        "name": "Case Info:",
                        "value": ' '.join(args[1:]),
                        "inline": False
                    }
                ]
            }
        ]
    }

    try:
        req = requests.post(config['Discord Notifications']['url'], json=cn_message)
        print(req.status_code)
    except requests.exceptions.HTTPError as err:
        await ctx.reply("WARNING: Unable to send notification to Discord. Contact a cyberseal!")
        logging.error(f"Unable to notify Discord: {err}")
