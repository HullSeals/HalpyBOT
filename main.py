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
import asyncio
from aiohttp import web

from src.server import APIConnector, MainAnnouncer, HalpyClient

from src.packages.ircclient import HalpyBOT, pool
from src.packages.configmanager import config

logging.basicConfig(format='%(levelname)s\t%(name)s\t%(message)s',
                    level=logging._nameToLevel.get(config.get('Logging', 'level', fallback='DEBUG'), logging.DEBUG))

def _start_bot():
    """Starts HalpyBOT with the specified config values."""
    from src import commands  # pylint disable=unused-import

    bot_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(bot_loop)
    loop = asyncio.get_event_loop()

    client = HalpyBOT(
        nickname=config['IRC']['nickname'],
        sasl_identity=config['SASL']['identity'],
        sasl_password=config['SASL']['password'],
        sasl_username=config['SASL']['username'],
        eventloop=loop
    )

    MainAnnouncer.client = client
    HalpyClient.client = client

    pool.connect(client, config['IRC']['server'], config['IRC']['port'],
                 tls=config.getboolean('IRC', 'useSsl'), tls_verify=False)
    pool.handle_forever()

def _start_server():
    server_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(server_loop)
    loop = asyncio.get_event_loop()

    web.run_app(APIConnector)


if __name__ == "__main__":
    bthread = threading.Thread(target=_start_bot, name="BotThread", daemon=True)
    bthread.start()
    sthread = threading.Thread(target=_start_server(), name="ServerThread", daemon=True)
    sthread.start()
