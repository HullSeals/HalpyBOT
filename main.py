"""
HalpyBOT v1.2.3

> For the Hull Seals, with a boot to the head
Rixxan

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import pydle
import logging
import src.packages.command.commandhandler as commandhandler
import asyncio
import signal
import functools
from src.packages.announcer import announcer
from src.packages.database import facts
import configparser

config = configparser.ConfigParser()
config.read('config/config.ini')

channels = [entry.strip() for entry in config.get('Channels', 'ChannelList').split(',')]

logging.basicConfig(format='%(levelname)s\t%(name)s\t%(message)s',
                    level=logging._nameToLevel.get(config.get('Logging', 'level', fallback='DEBUG'), logging.DEBUG))


class HalpyBOT(pydle.Client):
    # Join the Server and Channels and OperLine
    async def on_connect(self):
        await super().on_connect()
        await facts.on_connect()
        print("Fact module loaded successfully")
        await self.raw(f"OPER {config['IRC']['operline']} {config['IRC']['operlinePassword']}\r\n")
        logging.info("Connected")
        print("Connected!")
        for channel in channels:
            await self.join(channel)
            logging.info(f"Joining {channel}")
        await offlinecheck()

    async def on_channel_message(self, target, nick, message):
        await super().on_channel_message(target, nick, message)
        await commandhandler.on_channel_message(self, target, nick, message)
        nicks = [entry.strip() for entry in config.get('Announcer', 'nicks').split(',')]
        if target in config['Announcer']['channel'] and nick in nicks:
            await announcer.on_channel_message(self, target, nick, message)

    async def on_private_message(self, target, nick, message):
        await super().on_private_message(target, nick, message)
        await commandhandler.on_private_message(self, target, nick, message)

    async def reply(self, channel: str, sender: str, in_channel: bool, message: str):
        if in_channel:
            await self.message(channel, message)
        else:
            await self.message(sender, message)


# Define the Client, mostly pulled from config.ini
client = HalpyBOT(
    config['IRC']['nickname'],
    sasl_identity=config['SASL']['identity'],
    sasl_password=config['SASL']['password'],
    sasl_username=config['SASL']['username']
)


async def start():
    await client.connect(config['IRC']['server'], config['IRC']['port'],
                         tls=config.getboolean('IRC', 'useSsl'), tls_verify=False)

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


offline_mode: bool = config.getboolean('Offline Mode', 'Enabled')

om_channels = [entry.strip() for entry in config.get('Offline Mode', 'announce_channels').split(',')]


async def offlinecheck():
    logging.debug("STARTING OFFLINECHECK")
    try:
        loop = asyncio.get_running_loop()
        while True:
            if offline_mode is True:
                for ch in om_channels:
                    await client.message(ch, "HalpyBOT in OFFLINE mode! Database connection unavailable. Contact a CyberSeal.")
            await asyncio.sleep(300)
            if offline_mode is False:
                await asyncio.sleep(300)
    except asyncio.exceptions.CancelledError:
        pass



LOOP = None

if __name__ == "__main__":
    LOOP = asyncio.get_event_loop()
    for signame in ('SIGINT', 'SIGTERM', 'SIGUSR2'):
        LOOP.add_signal_handler(getattr(signal, signame),
                                functools.partial(asyncio.ensure_future,
                                                  shutdown(getattr(signal, signame), LOOP)))
    LOOP.run_until_complete(start())
    LOOP.run_forever()
