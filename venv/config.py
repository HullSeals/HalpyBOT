import logging

class IRC:
    server = 'irc.hullseals.space'
    port = 6697
    useSsl = True
    nickname = 'HalpyBOT_DEV'
    commandPrefix = '!'
    operline = '' # Removed for Git push.
    operlinePassword = '' # Removed for Git push.

class Logging:
    filename = 'halpybot.log'
    level = logging.DEBUG

class ChannelArray:
    channels = ["#bot-test", "#seal-bob"] # This *should* work and be an easy-expand list of channels to join. It didn't want to work tho.
