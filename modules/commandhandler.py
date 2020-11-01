from modules.facts.fact import recite_fact
from config import IRC
import main
from .announcer import manual_case
from .util import shutdown

# Please please leave this intact, even if empty
commandList = {
    "manualcase": manual_case.manual_case,
    "mancase": manual_case.manual_case,
    "manualfish": manual_case.manual_kingfisher,
    "manfish": manual_case.manual_kingfisher,
}

commandPrivateOnly = {
    "shutdown": shutdown.shutdown
}

factlist = [
    "go",
    "beacon",
    "cbinfo",
    "cbmining",
    "clientinfo",
    "escapeneutron",
    "paperwork",
    "pw",
    "clear",
    "pcfr",
    "psfr",
    "xbfr",
    "stuck",
    "prep",
    "verify",
    "chatter",
    "join",
    "bacon",
    "fuel",
    "cmdlist",
    "welcome",
    "tos",
    "highg",
    "synth",
    "fact_test"
]

factPrivateOnly = [
    "help",
    "about"
]


async def on_channel_message(bot: main, channel: str, sender: str, message: str):
    if message.startswith(IRC.commandPrefix):
        parts = message[1:].split(" ")
        command = parts[0]
        args = parts[1:]
        messagemode = 1
        if command in commandList:
            return await commandList[command](bot, channel, sender, args, messagemode)
        elif command in factlist:
            return await recite_fact(bot, channel, sender, args, messagemode, fact=str(command))
        else:
            return


async def on_private_message(bot: main, channel: str, sender: str, message: str):
    if message.startswith(IRC.commandPrefix):
        parts = message[1:].split(" ")
        command = parts[0]
        args = parts[1:]
        messagemode = 2
        if command in commandList.keys():
            return await commandList[command](bot, channel, sender, args, messagemode)
        elif command in commandPrivateOnly.keys():
            return await commandPrivateOnly[command](bot, channel, sender, args, messagemode)
        elif command in factlist or factPrivateOnly:
            return await recite_fact(bot, channel, sender, args, messagemode, fact=str(command))
        else:
            return
