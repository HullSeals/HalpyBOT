"""
> For the Hull Seals, with a boot to the head
Rixxan

start.py - HalpyBOT startup script

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
import asyncio
import os
import signal
from logging import Handler, basicConfig, getLevelName
import sys
from os import path, mkdir
from loguru import logger
from aiohttp import web

# noinspection PyUnresolvedReferences
from halpybot import commands
from halpybot.packages.configmanager import config
from halpybot.packages.ircclient import HalpyBOT
from halpybot.server import APIConnector


class InterceptHandler(Handler):
    """Grab standard logging and sends to loguru"""

    def emit(self, record):
        """Intercepts standard logging messages for the purpose of sending them to loguru"""
        logger_opt = logger.opt(depth=1, exception=record.exc_info)
        logger_opt.log(getLevelName(record.levelno), record.getMessage())


def logging_format():
    """
    Configure the logging system, utilizing Loguru
    """
    # Configure Logging File Name and Levels
    log_file: str = config["Logging"]["log_file"]
    cli_level = config["Logging"]["cli_level"]
    file_level = config["Logging"]["file_level"]

    # Attempt to create log folder and path if it doesn't exist
    try:
        log_folder = path.dirname(log_file)
        if not path.exists(log_folder):
            mkdir(log_folder)
    except PermissionError:
        logger.exception(
            "Unable to create log folder. Does this user have appropriate permissions?"
        )
        sys.exit()

    # Set the log format
    formatter = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | {extra} | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    # Hook logging intercept
    basicConfig(handlers=[InterceptHandler()], level=0)

    # Remove default logger
    logger.remove()

    # Add File Logger
    logger.add(
        log_file,
        level=file_level,
        format=formatter,
        rotation="500 MB",
        compression="zip",
        retention=90,
        filter=lambda record: "task" not in record["extra"]
        or (record["extra"]["task"] != "API" and record["extra"]["task"] != "API"),
    )

    # # Add API connection Logger
    logger.add(
        "logs/connection.log",
        level=file_level,
        format=formatter,
        rotation="500 MB",
        compression="zip",
        retention=90,
        filter=lambda record: "task" in record["extra"]
        and record["extra"]["task"] == "API",
    )

    # Add unauthorized command Logger
    logger.add(
        "logs/command_access.log",
        level=file_level,
        format=formatter,
        rotation="500 MB",
        compression="zip",
        retention=90,
        filter=lambda record: "task" in record["extra"]
        and record["extra"]["task"] == "Command",
    )

    # Add CLI Logger
    logger.add(sys.stdout, level=cli_level, format=formatter)


async def main():
    """
    The main startup script for HalpyBOT, called by the entry point
    """
    logging_format()
    client = HalpyBOT(
        nickname=config["IRC"]["nickname"],
        sasl_identity=config["SASL"]["identity"],
        sasl_password=config["SASL"]["password"],
        sasl_username=config["SASL"]["username"],
    )
    runner = web.AppRunner(APIConnector)
    runner.app["botclient"] = client
    await runner.setup()
    site = web.TCPSite(runner, "localhost", port=int(config["API Connector"]["port"]))
    await site.start()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(
        client.connect(
            hostname=config["IRC"]["server"],
            port=config["IRC"]["port"],
            tls=config.getboolean("IRC", "usessl"),
            tls_verify=False,
        ),
        loop=loop,
    )
    while True:
        await asyncio.sleep(3600)


# Global Entry Point
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        os.kill(os.getpid(), signal.SIGTERM)
