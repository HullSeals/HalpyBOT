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

user.py - User dataclass

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""


from __future__ import annotations

from typing import Union, Optional
from dataclasses import dataclass
from ..command.commandhandler import Context


@dataclass(frozen=True)
class User:
    oper: bool
    idle: int
    away: bool
    away_message: Optional[str]
    username: str
    hostname: str
    realname: str
    identified: bool
    channels: set
    server: str
    server_info: str
    secure: bool
    account: Optional[str]
    nickname: str

    @classmethod
    async def get_info(cls, ctx: Context, nickname: str) -> Optional[User]:
        # fetch the user object from pydle
        data = await ctx.bot.whois(nickname)

        # if we got a object back
        if data:
            return cls(**data, nickname=nickname)
        else:
            return None

    @classmethod
    def process_vhost(cls, vhost: Union[str, None]) -> Optional[str]:
        # sanity check
        if vhost is None:
            return None
        # RixxanCheck(TM)
        if vhost == "Rixxan.admin.hullseals.space":
            return vhost
        # sanity / security check
        if not vhost.endswith(".hullseals.space"):
            return None

        # identify the role
        host = vhost.rsplit(".", 3)[-3]

        # return the corresponding vhost
        return f"{host}.hullseals.space"

    @classmethod
    async def get_channels(cls, ctx: Context, nick: str) -> Optional[list]:
        user = await ctx.bot.whois(nick)
        channels = user['channels']
        return [ch.translate({ord(c): None for c in '+%@&~'}).lower() for ch in channels]
