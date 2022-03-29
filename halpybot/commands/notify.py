"""
HalpyBOT v1.6

notify.py - AWS SNS Interface

Copyright (c) 2022 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import time
from typing import List
from loguru import logger
from ..packages import notify
from ..packages.checks import Require, Moderator, Admin, Owner, Pup
from ..packages.command import CommandGroup, Commands, get_help_text
from ..packages.configmanager import config
from ..packages.models import Context


NotifyInfo = CommandGroup()
NotifyInfo.add_group("notifyinfo", "notificationinfo")


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
        results = await notify.list_topics()
    except notify.SNSError:
        logger.exception("Unable to get group data from AWS.")
        return await ctx.reply(
            "Unable to retrieve group data from AWS servers, "
            "poke Rixxan if this keeps occurring"
        )

    if len(results) == 0:
        return await ctx.reply(
            "No groups currently registered, contact Rixxan if you suspect "
            "this may be an error."
        )
    return await ctx.reply(
        f"Registered notification groups: {', '.join(group for group in results)}"
    )


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
        return await ctx.reply(get_help_text("notifyinfo details"))

    group = args[0].lower().strip()

    if group in ["staff", "moderators", "hull-seals-staff"]:
        group = "staff"
    elif group in ["cybers", "cyberseals"]:
        group = "cybers"
    else:
        return await ctx.reply(f"Invalid group given: {group}.")

    try:
        results = await notify.list_sub_by_topic(config["Notify"][group])
        if len(results) == 0:
            return await ctx.reply("No users currently subscribed to that group.")
        results = str(results)
        return await ctx.reply(
            f"Following endpoints are subscribed to group {group}: {results}"
        )

    except notify.SNSError:
        logger.exception("Unable to get info from AWS.")
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

    if len(args) <= 1:
        return await ctx.reply(get_help_text("addsub"))

    group = args[0].lower().strip()

    if group in ["staff", "moderators", "hull-seals-staff"]:
        group = "staff"
    elif group in ["cybers", "cyberseals"]:
        group = "cybers"
    else:
        return await ctx.reply(
            "Please specify a valid group, for example: 'moderators', 'cyberseals'"
        )
    try:
        await notify.subscribe(config["Notify"][group], args[1])
        return await ctx.reply(f"Subscription {args[1]} added to group {group}")
    except ValueError:
        return await ctx.reply(
            "Please specify a valid email address or phone number"
            "in international format."
        )
    except notify.SubscriptionError:
        logger.exception("Unable to add subscription.")
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

    with NotificationLock() as lock:
        if not lock.locked:

            subject, topic, message = await format_notification(
                "OpSignal", "staff", ctx.sender, args
            )
            try:
                await notify.send_notification(topic, message, subject)
            except notify.NotificationFailure:
                logger.exception("Notification not sent! I hope it wasn't important...")
                return ctx.reply("Unable to send the notification!")
            return ctx.reply(
                f"Message Sent to group {topic.split(':')[5]}. Please only send one message per issue!"
            )

        else:
            return await ctx.reply(
                "Someone already called less than 5 minutes ago. hang on, staff is responding."
            )


@Commands.command(
    "summontech", "calltech", "shitsfucked", "shitsonfireyo", "cybersignal", "cybersig"
)
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

    with NotificationLock() as lock:
        if not lock.locked:

            subject, topic, message = await format_notification(
                "CyberSignal", "cybers", ctx.sender, args
            )
            try:
                await notify.send_notification(topic, message, subject)
            except notify.NotificationFailure:
                logger.exception("Notification not sent! I hope it wasn't important...")
                return ctx.reply("Unable to send the notification!")
            return await ctx.reply(
                f"Message Sent to group {topic.split(':')[5]}. Please only send one message per issue!"
            )

        else:
            return await ctx.reply(
                "Someone already called less than 5 minutes ago. hang on, staff is responding."
            )


async def format_notification(notify_type, group, sender, message):
    """
    Format the notification to be sent to Seal Staff

    Args:
        notify_type (str): Type of signal being sent.
        group (str): Which group is being contacted.
        sender (str): Who is sending the notification.
        message (List[str]): Content of the message being sent.

    Returns:
        (tuple): Tuple with strings `subject`, `topic` and `message`
    """
    subject = f"HALPYBOT: {notify_type} Used"
    topic = config["Notify"][f"{group}"]
    message = " ".join(message)
    message = f"{notify_type} used by {sender}: {message}"
    return subject, topic, message


class NotificationLock:

    _timer = 0

    def __init__(self):
        """
        Create new context manager for the timed notification lock
        """
        self.locked = False
        # Check if last staff call was < 5 min ago
        if NotificationLock._timer != 0 and time.time() < NotificationLock._timer + int(
            config["Notify"]["timer"]
        ):
            self.locked = True
        NotificationLock._timer = time.time()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self
