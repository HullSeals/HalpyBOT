"""
This file uses Open Source components.
You can find the source code of their open source projects along with license
information below. We acknowledge and are grateful to these developers for their contributions to open source.

Project: SPARK / pipsqueak3 https://github.com/FuelRats/pipsqueak3
License: https://github.com/FuelRats/pipsqueak3/blob/develop/LICENSE

BSD 3-Clause License
Copyright (c) 2018, The Fuel Rats Mischief
All rights reserved.

HalpyBOT v1.6

mock_halpy.py - A Fully-Lobotimized Version of HalpyBOT for Tests

Copyright (c) 2022 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
from halpybot.packages.ircclient import HalpyBOT


class TestBot(HalpyBOT):
    """A Fully-Lobotimized Version of HalpyBOT"""

    # First, Grab the stuff from the HalpyBOT class.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # We also need a new sent messages holding pen
        self.sent_messages = []
        self.users = {
            "it_me[BOT]": {
                "nickname": "it_me[BOT]",
                "username": "test_bot",
                "hostname": "bots.hullseals.space",
                "away": False,
                "away_message": None,
                "account": None,
                "identified": True,
                "realname": "Gritty",
            },
            "generic_seal": {
                "nickname": "generic_seal",
                "username": "generic_seal",
                "hostname": "generic_seal@generic_seal.seal.hullseals.space",
                "away": False,
                "away_message": None,
                "account": None,
                "identified": True,
                "realname": "generic_seal",
            },
        }

    async def message(self, target: str, message: str):
        self.sent_messages.append({"target": target, "message": message})

    async def whois(self, name: str) -> dict:
        if name in self.users:
            return self.users[name]

    @classmethod
    def is_channel(cls, channel: str):
        return channel[0] in ("#", "&")

    async def connect(self):
        """Pydle connect override to prevent the mock accidently connecting to a server"""
        raise RuntimeWarning(
            "Connection to a server disallowed in instances of the mock bot."
        )
