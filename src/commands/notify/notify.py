"""
HalpyBOT v1.4

notify.py - AWS SNS Interface

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import time

from ...packages import notify
from ...packages.checks import *
from ...packages.command import CommandGroup, Commands
from ...packages.configmanager import config
import logging

NotifyInfo = CommandGroup()
NotifyInfo.add_group("notifyinfo", "notificationinfo")

# Set default value. This was originally Null but pylint didn't like that. Epoch gang!
timer = 0


@NotifyInfo.command("groups")
@require_permission(req_level="MODERATOR", message=DeniedMessage.MODERATOR)
@require_aws()
async def cmd_listgroups(ctx, args: List[str]):
    """
    List the existing notification groups.

    Usage: !notifyinfo groups
    Aliases: n/a
    """
    try:
        results = await notify.listTopics()
    except notify.SNSError:
        return await ctx.reply("Unable to retrieve group data from AWS servers, "
                               "poke Rixxan if this keeps occurring")

    if len(results) == 0:
        return await ctx.reply("No groups currently registered, contact Rixxan if you suspect "
                               "this may be an error.")
    else:
        return await ctx.reply(f"Registered notification groups: "
                               f"{', '.join(group for group in results)}")


@NotifyInfo.command("details", "endpoints")
@require_permission(req_level="OWNER", message=DeniedMessage.OWNER)
@require_dm()
@require_aws()
async def cmd_listnotify(ctx, args: List[str]):
    """
    List contact details of particular groups.

    Usage: !notifyinfo details [group]
    Aliases: notifyinfo endpoints
    """
    if not args:
        return await ctx.reply("No Group Given!")

    group = args[0].lower().strip()

    if group in ["staff", "moderators", "hull-seals-staff"]:
        group = "staff"
    elif group in ["cybers", "cyberseals"]:
        group = "cybers"
    else:
        return await ctx.reply(f"Invalid group given: {group}.")

    try:
        results = await notify.listSubByTopic(config['Notify'][group])
        if len(results) == 0:
            return await ctx.reply("No users currently subscribed to that group.")
        else:
            results = str(results)
            return await ctx.reply(f"Following endpoints are subscribed to group {group}: {results}")

    except notify.SNSError:
        return await ctx.reply("Unable to get info from AWS. Maybe on Console?")


@Commands.command("subnotify", "alertme", "addsub", "subscribe")
@require_permission(req_level="ADMIN", message=DeniedMessage.ADMIN)
@require_dm()
@require_aws()
async def cmd_subscribe(ctx, args: List[str]):
    """
    Add a user to a valid group

    Usage: !subscribenotify [group] [info]
    Aliases: !alertme, !addsub
    """
    if not args:
        return await ctx.reply("No Group Given!")

    group = args[0].lower().strip()

    if group in ["staff", "moderators", "hull-seals-staff"]:
        group = "staff"
    elif group in ["cybers", "cyberseals"]:
        group = "cybers"
    else:
        return await ctx.reply("Please specify a valid group, for example: "
                               "'moderators', 'cyberseals'")

    try:
        await notify.subscribe(config['Notify'][group], args[1])
    except ValueError:
        return await ctx.reply("Please specify a valid email address or phone number"
                               "in international format.")
    except notify.SubscriptionError:
        return await ctx.reply("Unable to add subscription, please contact Rixxan.")


@Commands.command("summonstaff", "callstaff", "opsig")
@require_permission(req_level="PUP", message=DeniedMessage.PUP)
@require_channel()
@require_aws()
async def cmd_notifystaff(ctx, args: List[str]):
    """
    Send a notification to the Cyberseals.

    Usage: !summonstaff [info]
    Aliases: !callstaff, !opsig
    """
    if time.time() < timer + 5:
        return await ctx.reply("Someone already called less than 5 minutes ago. "
                               "hang on, staff is responding.")
    subject = "HALPYBOT: OpSignal Used"
    topic = config['Notify']['staff']
    message = ' '.join(args)
    message = f"OPSIG used by {ctx.sender}: {message}"
    try:
        await notify.sendNotification(topic, message, subject)
    except notify.NotificationFailure:
        return await ctx.reply("Unable to send the notification!")
    return await ctx.reply(f"Message Sent to group {topic.split(':')[5]}. Please only send one message per issue!")


@Commands.command("summontech", "calltech", "shitsfucked", "cybersig")
@require_permission(req_level="PUP", message=DeniedMessage.PUP)
@require_channel()
@require_aws()
async def cmd_notifycybers(ctx, args: List[str]):
    """
    Send a notification to the Cyberseals.

    Usage: !summontech [info]
    Aliases:!calltech, !cybersig
    """
    global timer
    # Check if last opsig or cybersig was sent > 5 min ago
    # TODO move the minimum time between two notifications to config
    if time.time() < timer + 5:
        return await ctx.reply("Someone already called less than 5 minutes ago. "
                               "hang on, staff is responding.")
    subject = "HALPYBOT: CyberSignal Used"
    topic = config['Notify']['cybers']
    message = ' '.join(args)
    message = f"CYBERSIG used by {ctx.sender}: {message}"
    try:
        await notify.sendNotification(topic, message, subject)
    except notify.NotificationFailure:
        return await ctx.reply("Unable to send the notification!")
    return await ctx.reply(f"Message Sent to group {topic.split(':')[5]}. Please only send one message per issue!")
