"""
notify.py - AWS SNS Interface

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
from typing import List
import pendulum
from loguru import logger
from halpybot import config
from ..packages import notify
from ..packages.checks import Require, Moderator, Admin, Owner, Pup
from ..packages.command import CommandGroup, Commands, get_help_text
from ..packages.models import Context

NotifyInfo = CommandGroup()
NotifyInfo.add_group("notifyinfo", "notificationinfo")


class Timer:
    """Decorator Timer Class"""

    def __init__(self, ttl: pendulum.Duration):
        self.ttl = ttl
        self.last_call = None

    def __call__(self, func):
        async def wrapper(ctx, *args, **kwargs):
            """Decorator to Determine if a function is to be run by timer"""
            should_call: bool = False
            if self.last_call is None:
                should_call = True
            if (
                self.last_call is not None
                and pendulum.now(tz="utc") > self.last_call + self.ttl
            ):
                should_call = True
            if should_call:
                self.last_call = pendulum.now(tz="utc")
                return await func(ctx, *args, **kwargs)
            next_valid = self.last_call + self.ttl
            return await ctx.reply(
                f"Someone already called less than {config.notify.timer} minutes ago."
                f" Hang on, staff is responding. Try again at {next_valid.to_time_string()} UTC."
            )

        return wrapper


timer_filter = Timer(ttl=pendulum.Duration(minutes=config.notify.timer))


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
    if not args:
        return await ctx.reply(
            get_help_text(ctx.bot.commandsfile, "notifyinfo details")
        )

    group = args[0].casefold().strip()

    if group in {"staff", "moderators", "hull-seals-staff"}:
        group = config.notify.staff
    elif group in {"cybers", "cyberseals"}:
        group = config.notify.cybers
    else:
        return await ctx.reply(f"Invalid group given: {group!r}.")

    try:
        results = await notify.list_sub_by_topic(group)
        if not results:
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
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, "addsub"))

    group = args[0].casefold().strip()

    if group in {"staff", "moderators", "hull-seals-staff"}:
        group = config.notify.staff
    elif group in {"cybers", "cyberseals"}:
        group = config.notify.cybers

    else:
        return await ctx.reply(
            "Please specify a valid group, for example: 'moderators', 'cyberseals'"
        )
    try:
        await notify.subscribe(group, args[1])
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
@timer_filter
async def cmd_notifystaff(ctx: Context, args: List[str]):
    """
    Send a notification to the Admins and Moderators.

    Usage: !summonstaff [info]
    Aliases: !callstaff, !opsig
    """
    if len(args) == 0:
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, "opsignal"))

    subject, topic, message = await format_notification(
        "OpSignal", "staff", ctx.sender, args
    )
    try:
        await notify.send_notification(topic, message, subject)
    except notify.NotificationFailure:
        logger.exception("Notification not sent! I hope it wasn't important...")
        return await ctx.reply("Unable to send the notification!")
    return await ctx.reply(
        f"Message Sent to group {topic.split(':')[5]}. Please only send one message per issue!"
    )


@Commands.command(
    "summontech", "calltech", "shitsfucked", "shitsonfireyo", "cybersignal", "cybersig"
)
@Require.permission(Pup)
@Require.channel()
@Require.aws()
@timer_filter
async def cmd_notifycybers(ctx: Context, args: List[str]):
    """
    Send a notification to the Cyberseals.

    Usage: !summontech [info]
    Aliases:!calltech, !cybersig
    """

    if len(args) == 0:
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, "cybersignal"))

    subject, topic, message = await format_notification(
        "CyberSignal", "cybers", ctx.sender, args
    )
    try:
        await notify.send_notification(topic, message, subject)
    except notify.NotificationFailure:
        logger.exception("Notification not sent! I hope it wasn't important...")
        return await ctx.reply("Unable to send the notification!")
    return await ctx.reply(
        f"Message Sent to group {topic.split(':')[5]}. Please only send one message per issue!"
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
    # Sanity check, prevent sensitive information disclosure in case this field
    # somehow gets injected.
    if group not in config.notify.WHITELIST_GROUPS:
        logger.critical("Attempt to access a blacklisted field in HalpyConfig.notify.")
        raise AssertionError("unauthorized group.")
    if group == "cybers":
        topic = config.notify.cybers
    elif group == "staff":
        topic = config.notify.staff
    else:
        # this should be unreachable.
        raise AssertionError(f"unreachable 'group' variant {group!r} reached.")
    message = " ".join(message)
    message = f"{notify_type} used by {sender}: {message}"
    return subject, topic, message
