"""
checks.py - Check check check...

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import functools
from typing import List, Optional
from loguru import logger
from attrs import define
from halpybot import config
from ..models import User
from ..database import test_database_connection, NoDatabaseConnection


@define(frozen=True)
class Permission:
    """Reference a specific permission level"""

    vhost: str
    level: int
    msg: str


Bot = Permission(
    vhost="bots.hullseals.space",
    level=1,
    msg="You shouldn't be able to see this sanity check...",
)

Pup = Permission(
    vhost="pup.hullseals.space",
    level=1,
    msg="You need to be registered and logged in with NickServ to use this",
)

Drilled = Permission(
    vhost="seal.hullseals.space",
    level=2,
    msg="You have to be a drilled seal to use this!",
)

Moderator = Permission(
    vhost="moderator.hullseals.space", level=3, msg="Only moderators+ can use this."
)

Admin = Permission(
    vhost="admin.hullseals.space",
    level=4,
    msg="Denied! This is for your friendly neighbourhood admin",
)

Cyberseal = Permission(
    vhost="cyberseal.hullseals.space",
    level=5,
    msg="This can only be used by cyberseals.",
)

Cybermgr = Permission(
    vhost="cybersealmgr.hullseals.space",
    level=6,
    msg="You need to be a cyberseal manager for this.",
)

Owner = Permission(
    vhost="rixxan.admin.hullseals.space",
    level=7,
    msg="You need to be a Rixxan to use this",
)

_levels = {
    Bot.vhost: 1,
    Pup.vhost: 1,
    Drilled.vhost: 2,
    Moderator.vhost: 3,
    Admin.vhost: 4,
    Cyberseal.vhost: 5,
    Cybermgr.vhost: 6,
    Owner.vhost: 7,
}


def needs_permission(role: Permission, message: Optional[str] = None):
    """Require permission for a command

    Args:
        role (Permission): Required authorization level:
            `NONE`, `PUP`, `DRILLED`, `MODERATOR`, `ADMIN`, `CYBER`, `CYBERMGR`, `OWNER`
        message (str): Message we send when user does not have authorization.
            Default: `Access Denied.`

    """

    def decorator(function):
        @functools.wraps(function)
        async def guarded(ctx, args: List[str]):
            # Add Command Logger
            command_logger = logger.bind(task="Command")

            # Sanity check
            if not isinstance(role, Permission):
                raise ValueError("Permission must be of type 'Permission'")
            # Define required level
            required_level = role.level
            # Get role
            whois: Optional[User] = await User.get_info(ctx.bot, ctx.sender)
            vhost = User.process_vhost(whois.hostname)

            if vhost is None:
                command_logger.warning(
                    "Permission Error: {sender}!@{host} used {command} (Req: {req}) in {channel}",
                    sender=ctx.sender,
                    host=whois.hostname,
                    command=ctx.command,
                    req=required_level,
                    channel=ctx.channel,
                )
                return await ctx.reply(role.msg if message is None else message)

            # Find user level that belongs to vhost
            user_level = int(_levels[vhost])
            # If permission is not correct, send deniedMessage

            if user_level < required_level:
                # Log it and send off for the dashboard
                command_logger.warning(
                    "Permission Error: {sender}!@{host} used {command} (Req: {req}) in {channel}",
                    sender=ctx.sender,
                    host=whois.hostname,
                    command=ctx.command,
                    req=required_level,
                    channel=ctx.channel,
                )
                return await ctx.reply(role.msg if message is None else message)

            return await function(ctx, args)

        return guarded

    return decorator


def in_direct_message():
    """Require command to be executed in a Direct Message with the bot"""

    def decorator(function):
        @functools.wraps(function)
        async def guarded(ctx, args: List[str]):
            if ctx.in_channel:
                return await ctx.redirect(
                    "You have to run that command in DMs with me!"
                )
            return await function(ctx, args)

        return guarded

    return decorator


def in_channel():
    """Require command to be executed in an IRC channel"""

    def decorator(function):
        @functools.wraps(function)
        async def guarded(ctx, args: List[str]):
            if not ctx.in_channel:
                return await ctx.reply(
                    "You have to run this command in a channel! Aborted."
                )
            return await function(ctx, args)

        return guarded

    return decorator


def needs_aws():
    """Require Amazon Web Services configuration data to be specified in config"""

    def decorator(function):
        @functools.wraps(function)
        async def guarded(ctx, args: List[str]):
            if not config.notify.enabled:
                return await ctx.reply(
                    "Cannot comply: AWS Config data is required for this module."
                )
            return await function(ctx, args)

        return guarded

    return decorator


def needs_database():
    """Require a valid database connection and not in offline mode"""

    def decorator(function):
        @functools.wraps(function)
        async def guarded(ctx, args: List[str]):
            if config.offline_mode.enabled:
                logger.critical(config.offline_mode.enabled)
                return await ctx.reply("Cannot comply: Bot is in OFFLINE mode.")
            try:
                await test_database_connection(ctx.bot.engine)
            except NoDatabaseConnection:
                return await ctx.reply(
                    "Cannot comply: Database Error Detected. Entering OFFLINE mode."
                )
            return await function(ctx, args)

        return guarded

    return decorator
