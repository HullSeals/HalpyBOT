"""
Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.
Licensed under the BSD 3-Clause License.

Thanks to TFRM and Theunkn0wn1 for letting us use this.
"""


from __future__ import annotations

from typing import Union, Optional
from dataclasses import dataclass
from pydle import BasicClient


@dataclass(frozen=True)
class User:
    away: bool
    away_message: Optional[str]
    username: str
    hostname: str
    realname: str
    identified: bool
    account: Optional[str]
    nickname: str

    @classmethod
    async def get_info(cls, bot: BasicClient, nickname: str) -> Optional[User]:
        # fetch the user object from pydle
        data = bot.users.get(nickname.casefold(), None)

        # if we got a object back
        if data:
            return cls(**data)

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
