"""
HalpyBOT v1.4

> For the Hull Seals, with a boot to the head
Rixxan

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import logging
import threading
import pydle
import asyncio
from aiohttp import web

from src import commands

from src.server import APIConnector

from src.packages.ircclient import HalpyBOT
from src.packages.configmanager import config
from src.packages.command import Commands
from src.packages.facts import Facts

logging.basicConfig(format='%(levelname)s\t%(name)s\t%(message)s',
                    level=logging._nameToLevel.get(config.get('Logging', 'level', fallback='DEBUG'), logging.DEBUG))

pool = pydle.ClientPool()

# Define the Client, mostly pulled from config.ini
client = HalpyBOT(
    nickname=config['IRC']['nickname'],
    sasl_identity=config['SASL']['identity'],
    sasl_password=config['SASL']['password'],
    sasl_username=config['SASL']['username']
)


async def start():
    from src import commands  # pylint disable=unused-import

    # Set command- and fact handlers for client
    client.commandhandler = Commands
    client.commandhandler.facthandler = Facts
    await client.commandhandler.facthandler.fetch_facts(preserve_current=False)

    # Connect to server
    await client.connect(config['IRC']['server'], config['IRC']['port'],
                         tls=config.getboolean('IRC', 'useSsl'), tls_verify=False)
    await client.offline_monitor()


LOOP = None

if __name__ == "__main__":
    pool.connect(client, config['IRC']['server'], config['IRC']['port'],
                 tls=config.getboolean('IRC', 'useSsl'), tls_verify=False)
    bthread = threading.Thread(target=pool.handle_forever)
    bthread.start()
    client.commandhandler = Commands
    client.commandhandler.facthandler = Facts
    sthread = threading.Thread(target=web.run_app(APIConnector))
    sthread.start()
    asyncio.run(client.commandhandler.facthandler.fetch_facts(preserve_current=False))
