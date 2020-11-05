# This is an example file. To let it work, fill in all fields and rename this to config.py

import logging

class SASL:
    identity = 'HalpyBOT[YourNameHere]'
    username = 'YourNameHere'
    password = 'YourIRCPasswordHere'

class IRC:
    server = 'irc.hullseals.space'
    port = '+6697'
    useSsl = True
    nickname = 'HalpyBOT[Dev|YOURNAMEHERE]'
    commandPrefix = '!'
    operline = ''
    operlinePassword = ''

class Logging:
    filename = 'halpybot.log'
    level = logging.DEBUG

class ChannelArray:
    channels = ["#bot-test",
                "#seal-bob"]

class Announcer:
    channels = ["#case-notify-2"]
    nicks = ["WebHookBOT",
             "Rik079",
             "Feliksas",
             "Rixxan"]

class Database:
    user = "Some User"
    password = "SuperSecretPassword"
    host = "1.2.3.4"
    port = "3306"