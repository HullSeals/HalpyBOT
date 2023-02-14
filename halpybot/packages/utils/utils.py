"""
utils.py - miscellaneous utility functions

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import re
import json
import asyncio
import aiohttp
from loguru import logger
from halpybot import DEFAULT_USER_AGENT
from halpybot.commands.notify import format_notification, notify
from halpybot.packages.database import NoDatabaseConnection, test_database_connection
from halpybot import config
from halpybot.packages.models import User


def language_codes():
    """Get a dict of ISO-639-1 language codes

    Returns:
        (dict): A dictionary {2 letter abbreviation: name}

    """
    with open("data/languages/iso639-1.json", encoding="UTF-8") as file:
        langs = json.load(file)
        return langs


def strip_non_ascii(string: str):
    """Strip non-ASCII characters from a string

    Args:
        string (str): String that needs to be sanitized

    Returns:
        (tuple): A tuple with the values:

            - string (str): Stripped string
            - has_stripped (bool): True is characters were removed, else False

    """
    res = re.subn(r"[^\x00-\x7f]", r"", string)

    return res[0], bool(res != (string, 0))


async def web_get(uri: str, params=None, timeout=10):
    """
    Use aiohttp's client to send an HTTP GET request.
    uri: The URI/URL of the requested resource
    params: Any additional HTTP parameters to send
    timeout: Time in seconds before the server is deemed to have timed out
    """
    async with aiohttp.ClientSession(
        headers={"User-Agent": DEFAULT_USER_AGENT}
    ) as session:
        async with await session.get(
            uri,
            params=params,
            timeout=timeout,
        ) as response:
            responses = await response.json()
        return responses


async def task_starter(botclient):
    """
    Start the looping background tasks
    """
    [
        asyncio.create_task(task)
        for task in (
            _five_minute_task(botclient),
            # _ten_minute_task(),
            _one_hour_task(botclient),
            # _one_day_task(),
            _one_week_task(botclient),
        )
    ]


async def _five_minute_task(botclient):
    while True:
        await asyncio.sleep(300)
        if config.offline_mode.enabled:
            user = await User.get_info(botclient, botclient.nickname)
            if user.oper:
                await botclient.message(
                    "#opers", "WARNING: Offline Mode Enabled. Please investigate."
                )
            await asyncio.gather(
                *[
                    botclient.message(
                        channel, "WARNING: Offline Mode Enabled. Please investigate."
                    )
                    for channel in config.offline_mode.announce_channels
                ]
            )


# Reserved for Future Content
# async def _ten_minute_task(*args, **kwargs):
#     while True:
#         await asyncio.sleep(600)
#


async def _one_hour_task(botclient):
    while True:
        await asyncio.sleep(3600)
        try:
            await test_database_connection(botclient.engine)
        except NoDatabaseConnection:
            await botclient.message(
                config.offline_mode.announce_channels,
                "WARNING: Offline Mode Enabled. DB Ping Failure.",
            )


# Reserved for Future Content
# async def _one_day_task(*args, **kwargs):
#     while True:
#         await asyncio.sleep(86400)


async def _one_week_task(botclient):
    while True:
        await asyncio.sleep(604800)
        if not config.offline_mode.enabled:
            try:
                await botclient.facts.fetch_facts(
                    botclient.engine, preserve_current=True
                )
            except NoDatabaseConnection:
                config.offline_mode.enabled = True
                subject, topic, message = await format_notification(
                    "CyberSignal",
                    "cybers",
                    "HalpyBOT Monitoring System",
                    ["UFI Failure"],
                )
                try:
                    await notify.send_notification(topic, message, subject)
                except notify.NotificationFailure:
                    logger.exception(
                        "Notification not sent! I hope it wasn't important..."
                    )
