from modules.facts import fact
from config import IRC
import main

commandList = {
    "go": fact.go,
    "bacon": fact.bacon,
}

commandPrivateOnly = {
    "help": fact.help,
    "about": fact.about,
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
