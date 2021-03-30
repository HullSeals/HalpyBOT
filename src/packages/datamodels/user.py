"""
This file uses Open Source components.
You can find the source code of their open source projects along with license
information below. We acknowledge and are grateful to these developers for their contributions to open source.

Project: SPARK / pipsqueak3 https://github.com/FuelRats/pipsqueak3
License: https://github.com/FuelRats/pipsqueak3/blob/develop/LICENSE

BSD 3-Clause License
Copyright (c) 2018, The Fuel Rats Mischief
All rights reserved.

HalpyBOT v1.3

user.py - User dataclass

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""


from __future__ import annotations
from typing import Union, Optional
from dataclasses import dataclass
import pydle


@dataclass(frozen=True)
class User:
    """IRC User info

    Info about a user from WHOIS

    """
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
    async def get_info(cls, bot: pydle.Client, nickname: str) -> Optional[User]:
        """Get WHOIS info about a user

        Args:
            bot (pydle.Client): IRC Client
            nickname: User's nickname

        Returns:
            (Optional[User]): User object if successful, else None

        """
        # fetch the user object from pydle
        data = await bot.whois(nickname)

        # if we got a object back
        if data:
            return cls(**data, nickname=nickname)
        else:
            return None

    @classmethod
    # FIXME this should be Optional[str], but I don't want to touch it now since I don't
    # FIXME have time to test
    def process_vhost(cls, vhost: Union[str, None]) -> Optional[str]:
        """Get a users vhost-role

        Format <role>.hullseals.space

        Args:
            vhost (str): The full vhost of the user

        Returns:
            (Optional[str]): Vhost if identified, else None

        """
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
    async def get_channels(cls, bot: pydle.Client, nick: str) -> Optional[list]:
        """Get a list of channels a user is on

        Args:
            bot (pydle.Client): IRC Client
            nick (str): User's nickname

        Returns:
            (list): List of channels the user is on, without channel user status symbols

        """
        user = await bot.whois(nick)
        channels = user['channels']
        return [ch.translate({ord(c): None for c in '+%@&~'}).lower() for ch in channels]
