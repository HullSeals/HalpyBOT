"""
HalpyBOT v1.4

> For the Hull Seals, with a boot to the head
Rixxan

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

This module is due for a rewrite, and not documented

"""

import logging
import asyncio
import signal
import functools

from src.halpybot import HalpyBOT
from src.packages.configmanager import config

__version__ = "1.4.0"


logging.basicConfig(format='%(levelname)s\t%(name)s\t%(message)s',
                    level=logging._nameToLevel.get(config.get('Logging', 'level', fallback='DEBUG'), logging.DEBUG))


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
    client.version = __version__


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
