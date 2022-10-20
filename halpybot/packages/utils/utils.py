"""
utils.py - miscellaneous utility functions

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import re
import json
import aiohttp
import asyncio
from loguru import logger
from halpybot import DEFAULT_USER_AGENT
from halpybot.packages.database import NoDatabaseConnection
from halpybot.packages.facts import Facts


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


def timed_tasks(period):
    def scheduler(fcn):
        async def wrapper(*args, **kwargs):
            asyncio.create_task(fcn(*args, **kwargs))

        return wrapper

    return scheduler


async def task_starter():
    await _five_minute_task()
    await _ten_minute_task()
    await _one_hour_task()
    await _one_day_task()
    await _one_week_task()


@timed_tasks(300)
async def _five_minute_task(*args, **kwargs):
    while True:
        print("Five minute task running")
        await asyncio.sleep(300)


@timed_tasks(600)
async def _ten_minute_task(*args, **kwargs):
    while True:
        print("Ten minute task running")
        await asyncio.sleep(600)


@timed_tasks(3600)
async def _one_hour_task(*args, **kwargs):
    while True:
        print("One hour task running")
        await asyncio.sleep(360)


@timed_tasks(86400)
async def _one_day_task(*args, **kwargs):
    while True:
        print("One day task running")
        try:
            await Facts.fetch_facts(preserve_current=True)
        except NoDatabaseConnection:
            logger.exception("No Database Connection.")
        await asyncio.sleep(86400)


@timed_tasks(604800)
async def _one_week_task(*args, **kwargs):
    while True:
        print("One week task running")
        await asyncio.sleep(604800)
