from modules.facts.fact import recite_fact
from config import IRC
import main
from .announcer import manual_case
from .util import shutdown, utils
from .facts.fact import fact_index
from modules.facts import fact_management


commandList = {
    "manualcase": manual_case.manual_case,
    "mancase": manual_case.manual_case,
    "manualfish": manual_case.manual_kingfisher,
    "manfish": manual_case.manual_kingfisher,
    "shutdown": shutdown.shutdown,
    "ping": utils.ping,
    "say": utils.say,
    "test_command": utils.test_command,
    "allfacts": fact_management.allfacts,
    "fact_update": fact_management.manual_ufi,
    "ufi": fact_management.manual_ufi,
    "addfact": fact_management.addfact
}


async def on_channel_message(bot: main, channel: str, sender: str, message: str):
    if message.startswith(IRC.commandPrefix):
        parts = message[1:].split(" ")
        command = parts[0]
        args = parts[1:]
        in_channel = True
        if command in commandList:
            return await commandList[command](bot, channel, sender, args, in_channel)
        elif command in fact_index:
            return await recite_fact(bot, channel, sender, args, in_channel, fact=str(command))
        else:
            return


async def on_private_message(bot: main, channel: str, sender: str, message: str):
    if message.startswith(IRC.commandPrefix):
        parts = message[1:].split(" ")
        command = parts[0]
        args = parts[1:]
        in_channel = False
        if command in commandList.keys():
            return await commandList[command](bot, channel, sender, args, in_channel)
        elif command in fact_index:
            return await recite_fact(bot, channel, sender, args, in_channel, fact=str(command))
        else:
            return
