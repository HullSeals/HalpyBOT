"""
HalpyBOT v1.4

notify.py - AWS SNS Interface

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
from typing import List

from ...packages.notify import *
from ...packages.checks import *
from .. import Commands


@Commands.command("listgroups", "notifygroups")
@require_permission(req_level="MODERATOR", message=DeniedMessage.MODERATOR)
async def cmd_listgroups(ctx, args: List[str]):
    """
    List the existing notification groups.

    Usage: !listgroups
    Aliases: notifygroups
    """
    reply = await listTopics()
    return await ctx.reply(reply)


@Commands.command("listnotify")
@require_permission(req_level="OWNER", message=DeniedMessage.OWNER)
@require_dm()
async def cmd_listnotify(ctx, args: List[str]):
    """
    List contact details of particular groups.

    Usage: !listnotify [group]
    Aliases:
    """
    if not args:
        return await ctx.reply("No Group Given!")
    group = ctx.message.strip()
    group = group.lower()
    if group == "staff" or group == "moderators" or group == "hull-seals-staff":
        reply = await listSubByTopic(config['Notify']['staff'], "Hull-Seals-Staff")
    elif group == "cybers" or group == "cyberseals":
        reply = await listSubByTopic(config['Notify']['cybers'], "Cyberseals")
    else:
        reply = "Invalid group given. Aborting."

    return await ctx.reply(reply)


@Commands.command("subscribenotify", "alertme", "addsub")
@require_permission(req_level="ADMIN", message=DeniedMessage.ADMIN)
@require_dm()
async def cmd_subscribe(ctx, args: List[str]):
    """
    Add a user to a valid group

    Usage: !subscribenotify [group] [info]
    Aliases: !alertme, !addsub
    """
    if not args:
        return await ctx.reply("No Group Given!")
    if args[0].lower().strip() == "staff" or args[0].lower().strip() == "moderators" or args[0].lower().strip() == "hull-seals-staff":
        reply = await subscribe(config['Notify']['staff'], args[1].strip())
    elif args[0].lower().strip() == "cybers" or args[0].lower().strip() == "cyberseals":
        reply = await subscribe(config['Notify']['cybers'], args[1].strip())
    else:
        reply = "Invalid group given. Aborting."

    return await ctx.reply(reply)


@Commands.command("", "", "")
@require_permission(req_level="PUP", message=DeniedMessage.PUP)
async def cmd_notifytech(ctx, args: List[str]):
    """
    Send a notification to the Cyberseals.

    Usage: ! [info]
    Aliases:
    """


@Commands.command("", "", "")
@require_permission(req_level="PUP", message=DeniedMessage.PUP)
async def cmd_notifystaff(ctx, args: List[str]):
    """
    Send a notification to the Staff.

    Usage: ! [info]
    Aliases:
    """
