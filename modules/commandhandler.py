from modules.facts import fact
from config import IRC
import main

commandList = {
    "go": fact.go,
}

commandPrivateOnly = {}


async def on_channel_message(bot: main, channel: str, sender: str, message: str):
    if message.startswith(IRC.commandPrefix):
        parts = message[1:].split(" ")
        command = parts[0]
        args = parts[1:]
        # Start Commands
        if command in commandList:
            return await commandList[command](bot, channel, sender, args)
        else:
            return False
