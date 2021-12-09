"""
HalpyBOT v1.5

handler.py - Handler for IRC operator notices

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import pydle
import re


class NoticeRegistrationCollision(Exception):
    """
    Duplicate notice handler was created
    """


notices = {}
whitelist = ["OperServ",
             "HostServ",
             "NickServ",
             "ChanServ",
             "BotServ",
             "irc.hullseals.space",
             "services.hullseals.space",
             "Rik079", "Rik079[PC]",
             "Rixxan",
             "Feliksas"]


def listener(regex: str):
    """Add a notice handler by regex

    The regex string is stored as both itself and a compiled re object, in order
    to re

    Args:
        regex (str): Regex string that will invoke the function registered
        when matched by notice

    """

    def decorator(func):
        if regex in notices.keys():
            raise
        notices[re.compile(regex)] = func
        return func

    return decorator


async def on_notice(bot: pydle.Client, origin: str, target: str, message: str):
    """Process an incoming notice

    Args:
        bot (pydle.Client): IRC client receiving the notice
        origin: Source of the notice
        target: Target of the notice
        message: Content of the notice

    """
    if origin not in whitelist:
        pass  # Ignore whitelists from non-authorized sources to prevent abuse
    for listener_re in notices:
        match = re.match(listener_re, message)
        if match:
            return await notices[listener_re](bot, message, listener_re.search(message))
