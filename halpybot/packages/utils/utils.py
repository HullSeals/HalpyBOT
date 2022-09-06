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
from halpybot import DEFAULT_USER_AGENT


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
