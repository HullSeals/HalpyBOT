"""
HalpyBOT v1.4

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
from ..packages.command import CommandGroup, Commands
from ..packages.configmanager import config
from ..packages.utils import get_time_seconds
from ..packages.models import Context

NotifyInfo = CommandGroup()
NotifyInfo.add_group("notifyinfo", "notificationinfo")

# Set default value. This was originally Null but pylint didn't like that. Epoch gang!
timer = 0


@NotifyInfo.command("groups")
@Require.permission(Moderator)
@Require.AWS()
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
@Require.DM()
@Require.AWS()
async def cmd_listnotify(ctx: Context, args: List[str]):
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


@Commands.command("subnotify", "alertme", "addsub", "subscribe", "subscribenotify")
@Require.permission(Admin)
@Require.DM()
@Require.AWS()
async def cmd_subscribe(ctx: Context, args: List[str]):
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
        return await ctx.reply(f"Subscription {args[1]} added to group {group}")
    except ValueError:
        return await ctx.reply("Please specify a valid email address or phone number"
                               "in international format.")
    except notify.SubscriptionError:
        return await ctx.reply("Unable to add subscription, please contact Rixxan.")


@Commands.command("summonstaff", "callstaff", "opsignal")
@Require.permission(Pup)
@Require.channel()
@Require.AWS()
async def cmd_notifystaff(ctx: Context, args: List[str]):
    """
    Send a notification to the Admins and Moderators.

    Usage: !summonstaff [info]
    Aliases: !callstaff, !opsig
    """
    global timer
    # Check if last staff call was < 5 min ago
    if timer != 0 and time.time() < timer + int(await get_time_seconds(config['Notify']['timer'])):
        return await ctx.reply("Someone already called less than 5 minutes ago. "
                               "hang on, staff is responding.")
    timer = time.time()
    subject = "HALPYBOT: OpSignal Used"
    topic = config['Notify']['staff']
    message = ' '.join(args)
    message = f"OPSIG used by {ctx.sender}: {message}"
    try:
        await notify.sendNotification(topic, message, subject)
    except notify.NotificationFailure:
        return await ctx.reply("Unable to send the notification!")
    return await ctx.reply(f"Message Sent to group {topic.split(':')[5]}. Please only send one message per issue!")


@Commands.command("summontech", "calltech", "shitsfucked", "shitsonfireyo", "cybersignal")
@Require.permission(Pup)
@Require.channel()
@Require.AWS()
async def cmd_notifycybers(ctx: Context, args: List[str]):
    """
    Send a notification to the Cyberseals.

    Usage: !summontech [info]
    Aliases:!calltech, !cybersig
    """
    global timer
    # Check if last staff call was < 5 min ago
    if timer != 0 and time.time() < timer + int(await get_time_seconds(config['Notify']['timer'])):
        return await ctx.reply("Someone already called less than 5 minutes ago. "
                               "hang on, staff is responding.")
    timer = time.time()
    subject = "HALPYBOT: CyberSignal Used"
    topic = config['Notify']['cybers']
    message = ' '.join(args)
    message = f"CYBERSIG used by {ctx.sender}: {message}"
    try:
        await notify.sendNotification(topic, message, subject)
    except notify.NotificationFailure:
        return await ctx.reply("Unable to send the notification!")
    return await ctx.reply(f"Message Sent to group {topic.split(':')[5]}. Please only send one message per issue!")
