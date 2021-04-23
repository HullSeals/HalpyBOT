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


def _start_bot():
    from src import commands  # pylint disable=unused-import

    bot_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(bot_loop)
    loop = asyncio.get_event_loop()

    client.commandhandler = Commands
    client.commandhandler.facthandler = Facts
    loop.run_until_complete(client.commandhandler.facthandler.fetch_facts(preserve_current=False))

    pool.connect(client, config['IRC']['server'], config['IRC']['port'],
                 tls=config.getboolean('IRC', 'useSsl'), tls_verify=False)
    pool.handle_forever()


if __name__ == "__main__":
    bthread = threading.Thread(target=_start_bot)
    bthread.start()
    sthread = threading.Thread(target=web.run_app(APIConnector))
    sthread.start()
