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
                "hostname": "Toby_Charl@TobyCharlesPC.seal.hullseals.space",
                "away": False,
                "away_message": None,
                "account": None,
                "identified": True,
                "realname": "generic_seal",
            },
        }

    async def message(self, target: str, message: str):
        self.sent_messages.append({
            "target": target,
            "message": message
        })

    async def whois(self, name: str) -> dict:
        if name in self.users:
            return self.users[name]

    @classmethod
    def is_channel(cls, channel: str):
        return channel[0] in ("#", "&")

    async def connect(self):
        """Pydle connect override to prevent the mock accidently connecting to a server"""
        raise RuntimeWarning("Connection to a server disallowed in instances of the mock bot.")