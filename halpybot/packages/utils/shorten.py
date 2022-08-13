"""
shorten.py - YOURLS URL shortener

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
import aiohttp
from loguru import logger
from halpybot import DEFAULT_USER_AGENT
from ..configmanager import config


class YOURLSError(Exception):
    """
    Base class for YOURLS link errors
    """


class YOURLSNoResponse(YOURLSError):
    """
    An exception occurred while sending data to or receiving from a YOURLS API
    """


class YOURLSBadResponse(YOURLSError):
    """
    YOURLS returned an unprocessable response.
    """


async def shorten(url):
    """
    Shorten a given URL via a YOURLS passwordless API call

    Args:
        url (str): The URL to shorten

    Returns:
        surl (str): The shortened URL

    Raises:
        YOURLSNoResponse: YOURLS did not respond by the timeout.
    """
    if not url.lower().startswith("http"):
        url = "https://" + url

    try:
        async with aiohttp.ClientSession(
            headers={"User-Agent": DEFAULT_USER_AGENT}
        ) as session:
            async with await session.get(
                f"{config['YOURLS']['uri']}/yourls-api.php",
                params={
                    "signature": config["YOURLS"]["pwd"],
                    "action": "shorturl",
                    "format": "json",
                    "url": url,
                },
                timeout=10,
            ) as response:
                responses = await response.json()
    except aiohttp.ClientError as ex:
        logger.exception("YOURLS Did Not Respond")
        raise YOURLSNoResponse from ex

    if not responses:
        raise YOURLSNoResponse
    if "shorturl" not in responses:
        raise YOURLSBadResponse
    return responses["shorturl"]
