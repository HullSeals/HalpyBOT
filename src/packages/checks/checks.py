"""
This file uses Open Source components.
You can find the source code of their open source projects along with license
information below. We acknowledge and are grateful to these developers for their contributions to open source.

Project: SPARK / pipsqueak3 https://github.com/FuelRats/pipsqueak3
License: https://github.com/FuelRats/pipsqueak3/blob/develop/LICENSE

BSD 3-Clause License
Copyright (c) 2018, The Fuel Rats Mischief
All rights reserved.

HalpyBOT v1.4

checks.py - Check check check...

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""


import functools
from typing import List

from ..models import User
from ..configmanager import config, ConfigValidationFailure

levels = {
    "Rixxan.admin.hullseals.space": 7,
    "cybersealmgr.hullseals.space": 6,
    "cyberseal.hullseals.space": 5,
    "admin.hullseals.space": 4,
    "moderator.hullseals.space": 3,
    "seal.hullseals.space": 2,
    "pup.hullseals.space": 1,
    None: 0
}


requiredlevel = {
    "OWNER": 7,
    "CYBERMGR": 6,
    "CYBER": 5,
    "ADMIN": 4,
    "MODERATOR": 3,
    "DRILLED": 2,
    "PUP": 1,
    "NONE": 0,
}

class DeniedMessage:
    GENERIC = "Access denied."
    PUP = "You need to be registered and logged in with NickServ to use this"
    DRILLED = "You have to be a drilled seal to use this!"
    MODERATOR = "Only moderators+ can use this."
    ADMIN = "Denied! This is for your friendly neighbourhood admin"
    CYBER = "This can only be used by cyberseals."
    CYBERMGR = "You need to be a cyberseal manager for this."
    OWNER = "You need to be a Rixxan to use this"


def require_permission(req_level: str, message: str = "Access Denied."):
    """Require permission for a command

    Args:
        req_level (str): Required authorization level:
            `NONE`, `PUP`, `DRILLED`, `MODERATOR`, `ADMIN`, `CYBER`, `CYBERMGR`, `OWNER`
        message (str): Message we send when user does not have authorization.
            Default: `Access Denied.`

    """

    def decorator(function):
        @functools.wraps(function)
        async def guarded(ctx, args: List[str]):
            # Get role
            whois = await User.get_info(ctx.bot, ctx.sender)
            modes = User.process_vhost(whois.hostname)
            # Find user level
            userlevel = levels[modes]
            # Convert required permission to level
            level = int(requiredlevel[req_level])
            # If permission is not correct, send deniedMessage
            if userlevel < level:
                return await ctx.reply(message)
            else:
                return await function(ctx, args)

        return guarded

    return decorator


def require_dm():
    """Require command to be executed in a Direct Message with the bot"""

    def decorator(function):
        @functools.wraps(function)
        async def guarded(ctx, args: List[str]):
            if ctx.in_channel:
                return
            else:
                return await function(ctx, args)

        return guarded

    return decorator


def require_channel():
    """Require command to be executed in an IRC channel"""

    def decorator(function):
        @functools.wraps(function)
        async def guarded(ctx, args: List[str]):
            if ctx.in_channel is False:
                return
            else:
                return await function(ctx, args)

        return guarded

    return decorator

def require_aws():
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
