from modules.facts import fact
from config import IRC
import main


commandList = {
    # -- FACTS --
    "go": fact.go,
    "beacon": fact.beacon,
    "cbinfo": fact.cbinfo,
    "cbmining": fact.cbmining,
    "clientinfo": fact.clientinfo,
    "escapeneutron": fact.escapeneutron,
    "paperwork": fact.paperwork,
    "pw": fact.paperwork,
    "clear": fact.paperwork,
    "pcfr": fact.pcfr,
    "psfr": fact.psfr,
    "xbfr": fact.xbfr,
    "stuck": fact.stuck,
    "prep": fact.prep,
    "verify": fact.verify,
    "chatter": fact.chatter,
    "join": fact.join,
    "bacon": fact.bacon,
    "fuel": fact.fuel,
    "cmdlist": fact.cmdlist,
    "welcome": fact.welcome,
    "tos": fact.tos,
    "highg": fact.highg,
    "synth": fact.synth,
    "fact_test": fact.fact_test,
}

commandPrivateOnly = {
    # -- FACTS --
    "about": fact.about,
    "help": fact.help,
}


async def on_channel_message(bot: main, channel: str, sender: str, message: str):
    if message.startswith(IRC.commandPrefix):
        parts = message[1:].split(" ")
        command = parts[0]
        args = parts[1:]
        messagemode = 1
        # Start Commands
        if command in commandList:
            return await commandList[command](bot, channel, sender, args, messagemode)
        else:
            return False


async def on_private_message(bot: main, channel: str, sender: str, message: str):
    if message.startswith(IRC.commandPrefix):
        parts = message[1:].split(" ")
        command = parts[0]
        args = parts[1:]
        messagemode = 2
        # Start Commands
        if command in commandList:
            return await commandList[command](bot, channel, sender, args, messagemode)
        elif command in commandPrivateOnly:
            return await commandPrivateOnly[command](bot, channel, sender, args, messagemode)

