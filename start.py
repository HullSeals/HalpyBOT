"""
> For the Hull Seals, with a boot to the head
Rixxan

start.py - HalpyBOT startup script

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from logging import Handler, basicConfig, getLevelName
import sys
import threading
from os import path, mkdir
from loguru import logger
from aiohttp import web

# noinspection PyUnresolvedReferences
from halpybot import commands
from halpybot.packages.configmanager import config
from halpybot.packages.ircclient import client
from halpybot.server import APIConnector


class InterceptHandler(Handler):
    """Grab standard logging and sends to loguru"""

    def emit(self, record):
        """Intercepts standard logging messages for the purpose of sending them to loguru"""
        logger_opt = logger.opt(depth=1, exception=record.exc_info)
        logger_opt.log(getLevelName(record.levelno), record.getMessage())


def logging_format():
    # Configure Logging File Name and Levels
    logFile: str = config["Logging"]["log_file"]
    CLI_level = config["Logging"]["cli_level"]
    file_level = config["Logging"]["file_level"]

    # Attempt to create log folder and path if it doesn't exist
    try:
        logFolder = path.dirname(logFile)
        if not path.exists(logFolder):
            mkdir(logFolder)
    except PermissionError:
        logger.exception(
            "Unable to create log folder. Does this user have appropriate permissions?"
        )
        sys.exit()

    # Set the log format
    FORMATTER = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | {extra} | <cyan>{"
        "name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level> "
    )
    # Hook logging intercept
    basicConfig(handlers=[InterceptHandler()], level=0)

    # Remove default logger
    logger.remove()

    # Add File Logger
    logger.add(
        logFile,
        level=file_level,
        format=FORMATTER,
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
        format=FORMATTER,
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
        format=FORMATTER,
        rotation="500 MB",
        compression="zip",
        retention=90,
        filter=lambda record: "task" in record["extra"]
        and record["extra"]["task"] == "Command",
    )

    # Add CLI Logger
    logger.add(sys.stdout, level=CLI_level, format=FORMATTER)


def _start_bot():
    """Starts HalpyBOT with the specified config values."""
    client.run(
        hostname=config["IRC"]["server"],
        port=config["IRC"]["port"],
        tls=config.getboolean("IRC", "usessl"),
        tls_verify=False,
    )


if __name__ == "__main__":
    # Either the Bot, Webserver, or both need to be in their own threads isolated
    # This is due to how aiohttp handles asyncio and not sharing well
    logging_format()
    bthread = threading.Thread(target=_start_bot, name="BotThread", daemon=True)
    bthread.start()
    sthread = threading.Thread(
        target=web.run_app(app=APIConnector, port=int(config["API Connector"]["port"])),
        name="ServerThread",
        daemon=True,
    )
    sthread.start()
