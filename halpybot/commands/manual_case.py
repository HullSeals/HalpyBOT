"""
HalpyBOT v1.6

manual_case.py - Manual case creation module

Copyright (c) 2022 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List
import datetime
from loguru import logger
from ..packages.command import Commands, get_help_text
from ..packages.checks import Require, Drilled
from ..packages.models import Context, User
from ..packages.configmanager import config
from ..packages.announcer import send_webhook, WebhookSendError

webhook_id = config["Discord Notifications"]["webhook_id"]
webhook_token = config["Discord Notifications"]["webhook_token"]


@Commands.command("manualcase", "mancase", "manualfish", "manfish")
@Require.permission(Drilled)
@Require.channel()
async def cmd_manual_case(ctx: Context, args: List[str]):
    """
    Manually create a new case

    Usage: !manualcase [IRC name] [case info]
    Aliases: mancase, manualfish, manfish
    """
    if len(args) <= 1:
        return await ctx.reply(get_help_text("mancase"))

    # Shockingly, I couldn't find an easier way to do this. If you find one, let me know.
    try:
        await User.get_channels(ctx.bot, args[0])
    except AttributeError:
        return await ctx.reply(f"User {args[0]} doesn't appear to exist...")
    except KeyError:
        return await ctx.reply(get_help_text("mancase"))

    info = ctx.message
    logger.info(
        "Manual case by {sender} in {channel}", sender=ctx.sender, channel=ctx.channel
    )
    for channel in config["Manual Case"]["send_to"].split():
        await ctx.bot.message(
            channel, f"xxxx MANCASE -- NEWCASE xxxx\n{info}\nxxxxxxxx"
        )

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
                    {"name": "IRC Name:", "value": str(args[0]), "inline": False},
                    {
                        "name": "Case Info:",
                        "value": " ".join(args[1:]),
                        "inline": False,
                    },
                ],
            }
        ],
    }

    try:
        await send_webhook(
            hook_id=webhook_id, hook_token=webhook_token, body=cn_message
        )
    except WebhookSendError:
        await ctx.reply(
            "WARNING: Unable to send notification to Discord. Contact a cyberseal!"
        )


@Commands.command("tsping", "wssping")
@Require.permission(Drilled)
@Require.channel()
async def cmd_tsping(ctx: Context, args: List[str]):
    """
    Ping the 'Trained Seals' role on Discord. Annoying as duck and not to be used lightly

    Usage: !tsping [info]
    Aliases: wssping
    """
    if len(args) == 0:
        return await ctx.reply(get_help_text("tsping"))
    info = ctx.message

    cn_message = {
        "content": f"Attention, {config['Discord Notifications']['trainedrole']}! Seals are needed for this case.",
        "username": f"{ctx.sender}",
        "avatar_url": "https://hullseals.space/images/emblem_mid.png",
        "tts": False,
        "embeds": [
            {
                "title": "Dispatcher Needs Seals",
                "type": "rich",
                "timestamp": f"{datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')}",
                "color": 16093727,
                "footer": {
                    "text": f"Sent by {ctx.sender} from {ctx.channel}",
                    "icon_url": "https://hullseals.space/images/emblem_mid.png",
                },
                "fields": [
                    {"name": "Additional information", "value": info, "inline": False}
                ],
            }
        ],
    }

    try:
        await send_webhook(
            hook_id=webhook_id, hook_token=webhook_token, body=cn_message
        )
    except WebhookSendError:
        await ctx.reply(
            "WARNING: Unable to send notification to Discord. Contact a cyberseal!"
        )
    else:
        return await ctx.reply("Trained Seals ping sent out successfully.")
