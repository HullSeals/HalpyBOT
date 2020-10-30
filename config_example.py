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


