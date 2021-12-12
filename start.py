"""
HalpyBOT v1.5

> For the Hull Seals, with a boot to the head
Rixxan

start.py - HalpyBOT startup script

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import logging.handlers
import threading
import asyncio
import datetime
from os import path, mkdir
from aiohttp import web

from src.server import APIConnector, MainAnnouncer, HalpyClient

from src.packages.ircclient import HalpyBOT, pool
from src.packages.configmanager import config

logFile: str = config['Logging']['log_file']
CLI_level = config['Logging']['cli_level']
file_level = config['Logging']['file_level']

try:
    logFolder = path.dirname(logFile)
    if not path.exists(logFolder):
        mkdir(logFolder)
except PermissionError:
    print("Unable to create log folder. Does this user have appropriate permissions?")
    exit()

formatter = logging.Formatter('%(asctime)s\t%(levelname)s\t%(name)s\t%(message)s')

CLI_handler = logging.StreamHandler()
CLI_handler.setLevel(CLI_level)

# Will rotate log files every monday at midnight and keep at most 12 files,
# deleting the oldest, meaning logs are retained for 12 weeks (3 months)
# noinspection PyTypeChecker
file_handler = logging.handlers.TimedRotatingFileHandler(filename=logFile, when="w0", interval=14,
                                                         backupCount=12, utc=True, atTime=datetime.time())
file_handler.setLevel(file_level)

CLI_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

root = logging.getLogger()
root.setLevel(logging.DEBUG)

root.addHandler(CLI_handler)
root.addHandler(file_handler)


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
    asyncio.get_event_loop()

    web.run_app(app=APIConnector, port=int(config['API Connector']['port']))


if __name__ == "__main__":
    bthread = threading.Thread(target=_start_bot, name="BotThread", daemon=True)
    bthread.start()
    sthread = threading.Thread(target=_start_server(), name="ServerThread", daemon=True)
    sthread.start()
