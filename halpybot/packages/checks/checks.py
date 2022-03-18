"""
HalpyBOT v1.5.2

checks.py - Check check check...

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import functools
from typing import List
import logging

from ..models import User
from ..configmanager import config
from ..database import DatabaseConnection, NoDatabaseConnection, Grafana

logger = logging.getLogger(__name__)
logger.addHandler(Grafana)


class Permission:
    def __init__(self, vhost: str, level: int, msg: str):
        self.vhost = vhost
        self.level = level
        self.msg = msg


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
    Pup.vhost: 1,
    Drilled.vhost: 2,
    Moderator.vhost: 3,
    Admin.vhost: 4,
    Cyberseal.vhost: 5,
    Cybermgr.vhost: 6,
    Owner.vhost: 7,
}


def log_unauthorized(
    user: str, channel: str, command: str, args: List[str], required: int, provided: int
):
    """Emit an authorization incident to the dashboard log table

    Args:
        user (str): User that invoked the command
        channel (str): Channel the command was invoked in, username if in DM
        command (str): Used command
        args (list): List of arguments provided by the user
        required (int): Required permission level
        provided (int): Provided permission level

    """
    try:
        with DatabaseConnection() as db:
            cursor = db.cursor()
            cursor.callproc(
                "spCreateUnauthCmdAccess",
                [user, channel, command, " ".join(args), required, provided],
            )
    except NoDatabaseConnection:
        # TODO stash DB call and execute once we get back to online mode
        pass


class Require:
    @staticmethod
    def permission(role: Permission, message: str = None):
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
                # Sanity check
                if not isinstance(role, Permission):
                    raise ValueError("Permission must be of type 'Permission'")
                # Define required level
                required_level = role.level
                # Get role
                whois = await User.get_info(ctx.bot, ctx.sender)
                vhost = User.process_vhost(whois.hostname)

                if vhost is None:
                    await ctx.reply(role.msg if message is None else message)
                    logger.warning(
                        f"Permission error: {ctx.sender}!@{whois.hostname} used "
                        f"{ctx.command} (Req: {required_level}) in "
                        f"{ctx.channel}."
                    )
                    return log_unauthorized(
                        user=f"{ctx.sender}!@{whois.hostname}",
                        channel=ctx.channel,
                        command=ctx.command,
                        args=args,
                        required=required_level,
                        provided=0,
                    )

                # Find user level that belongs to vhost
                user_level = int(_levels[vhost])
                # If permission is not correct, send deniedMessage

                if user_level < required_level:
                    await ctx.reply(role.msg if message is None else message)
                    # Log it and send off for the dashboard
                    logger.warning(
                        f"Permission error: {ctx.sender}!@{whois.hostname} used "
                        f"{ctx.command} (Req: {required_level}) in "
                        f"{ctx.channel}."
                    )
                    return log_unauthorized(
                        user=f"{ctx.sender}!@{whois.hostname}",
                        channel=ctx.channel,
                        command=ctx.command,
                        args=args,
                        required=required_level,
                        provided=user_level,
                    )
                return await function(ctx, args)

            return guarded

        return decorator

    @staticmethod
    def direct_message():
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

    @staticmethod
    def channel():
        """Require command to be executed in an IRC channel"""

        def decorator(function):
            @functools.wraps(function)
            async def guarded(ctx, args: List[str]):
                if ctx.in_channel is False:
                    return await ctx.reply(
                        "You have to run this command in a channel! Aborted."
                    )
                else:
                    return await function(ctx, args)

            return guarded

        return decorator

    @staticmethod
    def aws():
        """Require Amazon Web Services configuration data to be specified in config"""

        def decorator(function):
            @functools.wraps(function)
            async def guarded(ctx, args: List[str]):
                if not config["Notify"]["secret"] or not config["Notify"]["access"]:
                    return await ctx.reply(
                        "Cannot comply: AWS Config data is required for this module."
                    )
                return await function(ctx, args)

            return guarded

        return decorator
