"""
HalpyBOT v1.5.2

notify.py - AWS SNS Interface

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import time
from typing import List

from ..packages import notify
from ..packages.checks import Require, Moderator, Admin, Owner, Pup
from ..packages.command import CommandGroup, Commands, get_help_text
from ..packages.configmanager import config
from ..packages.utils import get_time_seconds
from ..packages.models import Context

NotifyInfo = CommandGroup()
NotifyInfo.add_group("notifyinfo", "notificationinfo")

# Set default value. This was originally Null but pylint didn't like that. Epoch gang!
timer = 0


@NotifyInfo.command("groups")
@Require.permission(Moderator)
@Require.aws()
async def cmd_listgroups(ctx: Context, args: List[str]):
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
@Require.permission(Owner)
@Require.direct_message()
@Require.aws()
async def cmd_listnotify(ctx: Context, args: List[str]):
    """
    List contact details of particular groups.

    Usage: !notifyinfo details [group]
    Aliases: notifyinfo endpoints
    """
    if len(args) == 0:
        return await ctx.reply(get_help_text("notifyinfo"))

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


@Commands.command("subnotify", "alertme", "addsub", "subscribe", "subscribenotify")
@Require.permission(Admin)
@Require.direct_message()
@Require.aws()
async def cmd_subscribe(ctx: Context, args: List[str]):
    """
    Add a user to a valid group

    Usage: !subscribenotify [group] [info]
    Aliases: !alertme, !addsub
    """

    if len(args) == 0 or len(args) == 1:
        return await ctx.reply(get_help_text("addsub"))

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
        return await ctx.reply(f"Subscription {args[1]} added to group {group}")
    except ValueError:
        return await ctx.reply("Please specify a valid email address or phone number"
                               "in international format.")
    except notify.SubscriptionError:
        return await ctx.reply("Unable to add subscription, please contact Rixxan.")


@Commands.command("summonstaff", "callstaff", "opsignal", "opsig")
@Require.permission(Pup)
@Require.channel()
@Require.aws()
async def cmd_notifystaff(ctx: Context, args: List[str]):
    """
    Send a notification to the Admins and Moderators.

    Usage: !summonstaff [info]
    Aliases: !callstaff, !opsig
    """
    if len(args) == 0:
        return await ctx.reply(get_help_text("opsignal"))
    response = await format_notification("OpSignal", "staff", ctx.sender, args)
    return await ctx.reply(response)


@Commands.command("summontech", "calltech", "shitsfucked", "shitsonfireyo", "cybersignal", "cybersig")
@Require.permission(Pup)
@Require.channel()
@Require.aws()
async def cmd_notifycybers(ctx: Context, args: List[str]):
    """
    Send a notification to the Cyberseals.

    Usage: !summontech [info]
    Aliases:!calltech, !cybersig
    """

    if len(args) == 0:
        return await ctx.reply(get_help_text("cybersignal"))
    response = await format_notification("CyberSignal", "cybers", ctx.sender, args)
    return await ctx.reply(response)


async def format_notification(notify_type, group, sender, message):
    global timer
    # Check if last staff call was < 5 min ago
    if timer != 0 and time.time() < timer + int(await get_time_seconds(config['Notify']['timer'])):
        return "Someone already called less than 5 minutes ago. hang on, staff is responding."
    timer = time.time()
    subject = f"HALPYBOT: {notify_type} Used"
    topic = config['Notify'][f'{group}']
    message = ' '.join(message)
    message = f"{notify_type} used by {sender}: {message}"
    try:
        await notify.sendNotification(topic, message, subject)
    except notify.NotificationFailure:
        return "Unable to send the notification!"
    return f"Message Sent to group {topic.split(':')[5]}. Please only send one message per issue!"
