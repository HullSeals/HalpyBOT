"""
This file uses Open Source components.
You can find the source code of their open source projects along with license
information below. We acknowledge and are grateful to these developers for their contributions to open source.

Project: SPARK / pipsqueak3 https://github.com/FuelRats/pipsqueak3
License: https://github.com/FuelRats/pipsqueak3/blob/develop/LICENSE

BSD 3-Clause License
Copyright (c) 2018, The Fuel Rats Mischief
All rights reserved.

HalpyBOT v1.1

checks.py - Check check check...

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""


import functools
from typing import List
from ..datamodels.user import User

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
    "OWNER": '7',
    "CYBERMGR": '6',
    "CYBER": '5',
    "ADMIN": '4',
    "MODERATOR": '3',
    "DRILLED": '2',
    "PUP": '1',
    "NONE": '0',
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

    def decorator(function):
        @functools.wraps(function)
        async def guarded(ctx, args: List[str]):
            # Get role
            whois = await User.get_info(ctx.bot, nickname=ctx.sender)
            modes = User.process_vhost(whois.hostname)
            # Find user level
            userlevel = int(levels[modes])
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

    def decorator(function):
        @functools.wraps(function)
        async def guarded(ctx, args: List[str]):
            if ctx.in_channel is False:
                return
            else:
                return await function(ctx, args)

        return guarded

    return decorator
