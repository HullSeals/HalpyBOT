"""
HalpyBOT v1.5
Written by Rixxan and Rik079
For the Hull Seals
With a Boot to the Head.
"""

import pydle
import logging
import modules.commandhandler as commandhandler
import asyncio
import signal
import functools
from modules.announcer import announcer
from modules.facts import fact

from config import IRC, ChannelArray, SASL, Announcer

logging.basicConfig(format='%(asctime)s\t%(levelname)s\t%(name)s\t%(message)s', filename='halpybot.log', level=logging.DEBUG)


class HalpyBOT(pydle.Client):
    # Join the Server and Channels and OperLine
    async def on_connect(self):
        await super().on_connect()
        await fact.on_connect()
        print("Fact module loaded successfully")
        await self.raw(f"OPER {IRC.operline} {IRC.operlinePassword}\r\n")
        logging.info("Connected")
        print("Connected!")
        for channel in ChannelArray.channels:
            await self.join(channel)
            logging.info(channel)

    async def on_channel_message(self, target, nick, message):
        await super().on_channel_message(target, nick, message)
        await commandhandler.on_channel_message(self, target, nick, message)
        if target in Announcer.channels and nick in Announcer.nicks:
            await announcer.on_channel_message(self, target, nick, message)

    async def on_private_message(self, target, nick, message):
        await super().on_private_message(target, nick, message)
        await commandhandler.on_private_message(self, target, nick, message)

    async def reply(self, channel: str, sender: str, in_channel: bool, message: str):
        if in_channel:
            await self.message(channel, message)
        else:
            await self.message(sender, message)


# Define the Client, mostly pulled from config.py
client = HalpyBOT(
    IRC.nickname,
    sasl_identity=SASL.identity,
    sasl_password=SASL.password,
    sasl_username=SASL.username
)


async def start():
    await client.connect(IRC.server, IRC.port, tls=IRC.useSsl, tls_verify=False)

# Signal handler
async def shutdown(signal, loop):
    if signal != signal.SIGUSR2:
        print('caught {0}'.format(signal.name))
        logging.info('caught {0}'.format(signal.name))
    else:
        print('Received shutdown command')
        logging.info('Received shutdown command')

    await client.quit(message="Will be with you shortly, please hold!")

    tasks = [task for task in asyncio.all_tasks() if task is not
             asyncio.current_task()]
    list(map(lambda task: task.cancel(), tasks))
    results = await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

LOOP = None

if __name__ == "__main__":
    LOOP = asyncio.get_event_loop()
    for signame in ('SIGINT', 'SIGTERM', 'SIGUSR2'):
        LOOP.add_signal_handler(getattr(signal, signame),
                                functools.partial(asyncio.ensure_future,
                                                  shutdown(getattr(signal, signame), LOOP)))
    LOOP.run_until_complete(start())
    LOOP.run_forever()
