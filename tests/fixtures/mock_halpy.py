"""
This file uses Open Source components.
You can find the source code of their open source projects along with license
information below. We acknowledge and are grateful to these developers for their contributions to open source.

Project: SPARK / pipsqueak3 https://github.com/FuelRats/pipsqueak3
License: https://github.com/FuelRats/pipsqueak3/blob/develop/LICENSE

BSD 3-Clause License
Copyright (c) 2018, The Fuel Rats Mischief
All rights reserved.

mock_halpy.py - A Fully-Lobotimized Version of HalpyBOT for Tests

Copyright (c) The Hull Seals,
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
            "HalpyTest[BOT]": {
                "nickname": "HalpyTest[BOT]",
                "username": "HalpyTest[BOT]",
                "hostname": "HalpyTest[BOT]@bot.hullseals.space",
                "away": False,
                "away_message": None,
                "account": None,
                "identified": True,
                "realname": "HalpyTest[BOT]",
                "oper": True,
                "idle": 0,
                "server": "Blargh",
                "server_info": "BlargNet",
                "secure": True,
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
                "oper": False,
                "idle": 0,
                "server": "Blargh",
                "server_info": "BlargNet",
                "secure": True,
            },
            "guest_user": {
                "nickname": "guest_user",
                "username": "guest_user",
                "hostname": "guest_user@F19B0A02.B60B8A57.AA438FBA.IP",
                "away": False,
                "away_message": None,
                "account": None,
                "identified": False,
                "realname": "guest_user",
                "oper": False,
                "idle": 0,
                "server": "Blargh",
                "server_info": "BlargNet",
                "secure": True,
            },
            "some_pup": {
                "nickname": "some_pup",
                "username": "some_pup",
                "hostname": "some_pup@some_pup.pup.hullseals.space",
                "away": False,
                "away_message": None,
                "account": None,
                "identified": False,
                "realname": "some_pup",
                "oper": False,
                "idle": 0,
                "server": "Blargh",
                "server_info": "BlargNet",
                "secure": True,
            },
            "some_admin": {
                "nickname": "some_admin",
                "username": "some_admin",
                "hostname": "some_admin@some_admin.admin.hullseals.space",
                "away": False,
                "away_message": None,
                "account": None,
                "identified": True,
                "realname": "some_admin",
                "oper": True,
                "idle": 0,
                "server": "Blargh",
                "server_info": "BlargNet",
                "secure": True,
            },
            "some_cyber": {
                "nickname": "some_cyber",
                "username": "some_cyber",
                "hostname": "some_cyber@some_cyber.cyberseal.hullseals.space",
                "away": False,
                "away_message": None,
                "account": None,
                "identified": True,
                "realname": "some_cyber",
                "oper": True,
                "idle": 0,
                "server": "Blargh",
                "server_info": "BlargNet",
                "secure": True,
            },
            "Rixxan": {
                "nickname": "Rixxan",
                "username": "Rixxan",
                "hostname": "Rixxan@Rixxan.admin.hullseals.space",
                "away": False,
                "away_message": None,
                "account": None,
                "identified": True,
                "realname": "Rixxan",
                "oper": True,
                "idle": 0,
                "server": "Blargh",
                "server_info": "BlargNet",
                "secure": True,
            },
        }

    async def message(self, target: str, message: str):
        """Mock sending a message"""
        self.sent_messages.append({"target": target, "message": message})

    async def whois(self, nickname: str) -> dict:
        """Mock the return the details of a user"""
        if nickname in self.users:
            return self.users[nickname]

    @classmethod
    def is_channel(cls, channel: str):
        """Mock the response channel"""
        return channel[0] in "#&+."

    async def connect(self, **kwargs):
        """Pydle connect override to prevent the mock accidently connecting to a server"""
        raise RuntimeWarning(
            "Connection to a server disallowed in instances of the mock bot."
        )

    @property
    def engine(self):
        """Database Connection Engine"""
        return self._engine
