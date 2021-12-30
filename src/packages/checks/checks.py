"""
This file uses Open Source components.
You can find the source code of their open source projects along with license
information below. We acknowledge and are grateful to these developers for their contributions to open source.

Project: SPARK / pipsqueak3 https://github.com/FuelRats/pipsqueak3
License: https://github.com/FuelRats/pipsqueak3/blob/develop/LICENSE

BSD 3-Clause License
Copyright (c) 2018, The Fuel Rats Mischief
All rights reserved.

HalpyBOT v1.5

checks.py - Check check check...

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import functools
from typing import List

from ..models import User
from ..configmanager import config


class Permission:

    def __init__(self, vhost: str, level: int, msg: str):
        self.vhost = vhost
        self.level = level
        self.msg = msg


Pup = Permission(vhost="pup.hullseals.space",
                 level=1,
                 msg="You need to be registered and logged in with NickServ to use this")

Drilled = Permission(vhost="seal.hullseals.space",
                     level=2,
                     msg="You have to be a drilled seal to use this!")

Moderator = Permission(vhost="moderator.hullseals.space",
                       level=3,
                       msg="Only moderators+ can use this.")

Admin = Permission(vhost="admin.hullseals.space",
                   level=4,
                   msg="Denied! This is for your friendly neighbourhood admin")

Cyberseal = Permission(vhost="cyberseal.hullseals.space",
                       level=5,
                       msg="This can only be used by cyberseals.")

Cybermgr = Permission(vhost="cybersealmgr.hullseals.space",
                      level=6,
                      msg="You need to be a cyberseal manager for this.")

Owner = Permission(vhost="Rixxan.admin.hullseals.space",
                   level=7,
                   msg="You need to be a Rixxan to use this")

_levels = {
    Pup.vhost: 1,
    Drilled.vhost: 2,
    Moderator.vhost: 3,
    Admin.vhost: 4,
    Cyberseal.vhost: 5,
    Cybermgr.vhost: 6,
    Owner.vhost: 7,
}


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
                    return await ctx.reply(role.msg if
                                           message is None else message)
                # Find user level that belongs to vhost
                user_level = int(_levels[vhost])
                # If permission is not correct, send deniedMessage
                if user_level < required_level:
                    return await ctx.reply(role.msg if
                                           message is None else message)
                else:
                    return await function(ctx, args)

            return guarded

        return decorator

    @staticmethod
    def DM():
        """Require command to be executed in a Direct Message with the bot"""

        def decorator(function):
            @functools.wraps(function)
            async def guarded(ctx, args: List[str]):
                if ctx.in_channel:
                    return await ctx.redirect("You have to run that command in DMs with me!")
                else:
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
                    return await ctx.reply("You have to run this command in a channel! Aborted.")
                else:
                    return await function(ctx, args)

            return guarded

        return decorator

    @staticmethod
    def AWS():
        """Require Amazon Web Services configuration data to be specified in config"""

        def decorator(function):
            @functools.wraps(function)
            async def guarded(ctx, args: List[str]):
                if not config['Notify']['secret'] or not config['Notify']['access']:
                    return await ctx.reply("Cannot comply: AWS Config data is required for this module.")
                else:
                    return await function(ctx, args)

            return guarded

        return decorator
