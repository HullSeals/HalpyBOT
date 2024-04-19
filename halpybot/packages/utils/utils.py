"""
utils.py - miscellaneous utility functions

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from __future__ import annotations
import re
import json
import asyncio
from typing import Dict, Optional, Union, TYPE_CHECKING, Any, List
import aiohttp
from attr import evolve
from loguru import logger
from pendulum import now
from pydantic import SecretStr
from halpybot import DEFAULT_USER_AGENT
from halpybot.commands.notify import format_notification, notify
from halpybot.packages.exceptions import NotificationFailure
from halpybot.packages.command import get_help_text
from halpybot.packages.database import NoDatabaseConnection, test_database_connection
from halpybot import config
from halpybot.packages.models import User, Context

if TYPE_CHECKING:
    from halpybot.packages.ircclient import HalpyBOT


def language_codes() -> Dict[str, str]:
    """Get a dict of ISO-639-1 language codes

    Returns:
        (dict): A dictionary {2 letter abbreviation: name}

    """
    with open("data/languages/iso639-1.json", encoding="UTF-8") as file:
        return json.load(file)


def strip_non_ascii(string: str) -> tuple:
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


async def cache_prep(ctx: Context, args: List[str]):
    """Check if Cache Override should be set"""
    cache_override = False
    if len(args) == 0:
        return await ctx.reply(get_help_text(ctx.bot.commandsfile, ctx.command))
    if args[0] == "--new":
        cache_override = True
        del args[0]
        ctx = evolve(ctx, message=" ".join(args))
        if not ctx.message:
            return await ctx.reply(get_help_text(ctx.bot.commandsfile, ctx.command))
    message = ctx.message.strip()
    return message, cache_override


async def web_get(
    uri: str,
    params: Optional[Dict[str, Union[str, SecretStr, float]]] = None,
    timeout: int = 10,
) -> Dict[str, Any]:
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


async def new_case_check(botclient: HalpyBOT):
    """
    Check if a new case has not been welcomed yet.
    """
    board = botclient.board.by_id
    for case in board.values():
        if case.welcomed:
            continue
        await asyncio.gather(
            *[
                botclient.message(
                    channel,
                    f"Hey there, {case.irc_nick}! It seems we're a little short on Seals right now.\n"
                    f"Just hold tight and someone should be with you shortly!",
                )
                for channel in config.channels.rescue_channels
            ]
        )
        await asyncio.gather(
            *[
                botclient.message(
                    channel,
                    f"NEWCASE has not been welcomed. Seals, Please respond! Case ID: {case.board_id}",
                )
                for channel in config.channels.channel_list
            ]
        )
        new_notes = f"NEWCASE not welcomed. Reminder sent. - {botclient.nickname} ({now(tz='UTC').to_time_string()})"
        case.case_notes.append(new_notes)


async def task_starter(botclient: HalpyBOT):
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


async def _five_minute_task(botclient: HalpyBOT):
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
        await new_case_check(botclient)


# Reserved for Future Content
# async def _ten_minute_task(*args, **kwargs):
#     while True:
#         await asyncio.sleep(600)
#


async def _one_hour_task(botclient: HalpyBOT):
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


async def _one_week_task(botclient: HalpyBOT):
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
                except NotificationFailure:
                    logger.exception(
                        "Notification not sent! I hope it wasn't important..."
                    )


async def sys_cleaner(sys_name: str) -> str:
    """
    Attempt to match a given system string to the procedurally generated system naming convention.

    Args:
        sys_name (str): The given string which should be a system name.

    Returns:
        (str): The processed string, possibly matched to a procedurally generated naming convention.
    """
    orig_sys = sys_name
    sys_name = " ".join(sys_name.split())
    sys_name = sys_name.upper()

    # Remove any appended "SYSTEM" from the input.
    if sys_name.endswith("SYSTEM"):
        sys_name = (sys_name[:-6]).strip()

    try:
        if "-" in sys_name:
            sys_name_list = sys_name.split()
            sys_name = ""
            for index, block in enumerate(sys_name_list):
                sys_name += block + " "
                if "-" in block:
                    sys_name += sys_name_list[index + 1]
                    break

            swaps = {"0": "O", "1": "I", "5": "S", "8": "B"}
            unswaps = {value: key for key, value in swaps.items()}
            sys_name_parts = sys_name.split()

            # Final part is either LN or LN-N, so [1:] is N or N-N
            letter = sys_name_parts[-1][0]
            tmp = swaps[letter] if letter in swaps else letter
            for char in sys_name_parts[-1][1:]:
                if char in unswaps:
                    tmp += unswaps[char]
                else:
                    tmp += char
            sys_name_parts[-1] = tmp

            # This part it LL-L
            tmp = ""
            for char in sys_name_parts[-2]:
                if char in swaps:
                    tmp += swaps[char]
                else:
                    tmp += char
            sys_name_parts[-2] = tmp

            sys_name = " ".join(sys_name_parts)
    except IndexError:
        logger.info(
            "System cleaner thought {sys_name} was proc-gen and could not correct formatting",
            sys_name=sys_name,
        )
        return sys_name.strip()
    if sys_name == orig_sys:
        return sys_name.strip()
    logger.debug(
        "System cleaner produced {sys_name} from {orig_sys}",
        sys_name=sys_name,
        orig_sys=orig_sys,
    )
    return sys_name.strip()
