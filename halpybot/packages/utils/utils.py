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
from halpybot.packages.facts import Facts
from halpybot.packages.configmanager import config, config_write
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


async def get_time_seconds(time: str):
    """Get time in seconds from a hh:mm:ss format

    Args:
        time (str): Time, in a hh:mm:ss format

    Returns:
        (int): Time in seconds

    Raises:
        ValueError: String does not match required format

    """
    pattern = re.compile(r"(?P<hour>\d+):(?P<minutes>\d+):(?P<seconds>\d+)")
    if not re.match(pattern, time):
        raise ValueError("get_time_seconds input does not match hh:mm:ss format")
    res = pattern.search(time)
    counter = 0
    conversion_table = {"hour": 3600, "minutes": 60, "seconds": 1}
    for unit in conversion_table:
        value = int(res.group(unit))
        counter += value * conversion_table[unit]
    return str(counter)


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
            _one_week_task(),
        )
    ]


async def _five_minute_task(botclient, *args, **kwargs):
    while True:
        await asyncio.sleep(300)
        if config["Offline Mode"]["enabled"] == "True":
            user = await User.get_info(botclient, botclient.nickname)
            if user.oper:
                await botclient.message(
                    "#opers", "WARNING: Offline Mode Enabled. Please investigate."
                )
            await botclient.message(
                config["System Monitoring"]["message_channel"],
                "WARNING: Offline Mode Enabled. Please investigate.",
            )


# Reserved for Future Content
# async def _ten_minute_task(*args, **kwargs):
#     while True:
#         await asyncio.sleep(600)
#


async def _one_hour_task(botclient, *args, **kwargs):
    while True:
        await asyncio.sleep(3600)
        try:
            await test_database_connection()
        except NoDatabaseConnection:
            await botclient.message(
                config["System Monitoring"]["message_channel"],
                "WARNING: Offline Mode Enabled. DB Ping Failure.",
            )


# Reserved for Future Content
# async def _one_day_task(*args, **kwargs):
#     while True:
#         await asyncio.sleep(86400)


async def _one_week_task(*args, **kwargs):
    while True:
        await asyncio.sleep(604800)
        if config["Offline Mode"]["enabled"] != "True":
            try:
                await Facts.fetch_facts(preserve_current=True)
            except NoDatabaseConnection:
                config_write("Offline Mode", "enabled", "True")
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
