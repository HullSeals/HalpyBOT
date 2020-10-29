# This is an example file. To let it work, fill in all fields and rename this to config.py

import logging

class SASL:
    identity = ''
    username = ''
    password = ''

class IRC:
    server = 'irc.hullseals.space'
    port = 6697
    useSsl = True
    nickname = 'HalpyBOT_DEV'
    commandPrefix = '!'
    operline = ''
    operlinePassword = ''

class Logging:
    filename = 'halpybot.log'
    level = logging.DEBUG

class ChannelArray:
    channels = ["#bot-test",
                "#seal-bob"]


class Permissions:
    class PUP:
        level = 0
        vhosts = ["pup.hullseals.space"]

    class SEAL:
        level = 1
        vhosts = ["seal.hullseals.space"]

    class MODERATOR:
        level = 2
        vhosts = ["moderator.hullseals.space"]

    class ADMIN:
        level = 3
        vhosts = ["admin.hullseals.space"]

    class CYBER:
        level = 4
        vhosts = ["cyberseal.hullseals.space",
                  "cybersealmgr.hullseals.space"]

    class OWNER:
        level = 5
        vhosts = ["rixxan.admin.hullseals.space"]
