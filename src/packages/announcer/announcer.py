"""
HalpyBOT v1.5

announcer.py - Client announcement handler

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

"""

from __future__ import annotations
import pydle
import json
import re
import logging
from typing import List, Dict, Optional

from ..edsm import checklandmarks, get_nearby_system, NoResultsEDSM, EDSMLookupError, checkdssa, mistaken_char_subs
from .twitter import TwitterCasesAcc, TwitterConnectionError

logger = logging.getLogger(__name__)

cardinal_flip = {"North": "South", "NE": "SW", "East": "West", "SE": "NW",
                 "South": "North", "SW": "NE", "West": "East", "NW": "SE"}


class AnnouncementError(Exception):
    """
    Could not announce request
    """


class Announcer:

    def __init__(self, bot: Optional[pydle.Client] = None):
        """Initialize announcer

        The client is passed to this class by HalpyBOT even though
        that class itself does nothing with it, in order for us to
        call it easily

        Args:
            bot (pydle.Client): Bot client we make announcements with

        """
        self._client = bot
        self._announcements = {}
        # Load data
        with open('data/announcer/announcer.json', 'r') as cf:
            self._config = json.load(cf)
        # Create announcement objects and store them in dict
        for anntype in self._config['AnnouncerType']:
            self._announcements[anntype['ID']] = Announcement(
                ID=anntype['ID'],
                name=anntype['Name'],
                description=anntype['Description'],
                channels=anntype['Channels'],
                edsm=anntype['EDSM'],
                content=anntype['Content']
            )

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, client: Optional[pydle.Client]):
        self._client = client

    def rehash(self):
        pass

    async def announce(self, announcement: str, args: Dict):
        """Announce a new case

        Args:
            announcement: The type of announcement to make
            args: Arguments for the case announcement

        Returns:
            Nothing

        Raises:
            AnnouncementError: Case could not be announced for any reason

        """
        ann = self._announcements[announcement]
        # noinspection PyBroadException
        # We want to catch everything
        try:
            for ch in ann.channels:
                await self._client.message(ch, await ann.format(args))
            if "Platform" in args.keys():
                try:
                    await TwitterCasesAcc.tweet_case(announcement, args)
                except TwitterConnectionError:
                    return
        except Exception as ex:
            raise AnnouncementError(ex)


class Announcement:

    def __init__(self, ID: str, name: str, description: str,
                 channels: List[str], edsm: Optional[int], content: List[str]):
        """Create a new announceable object

        Args:
            ID (str): Announcement reference code, used by API
            name (str): Name, for reference only
            description (str): Description of the announcement
            channels (list of str): channels the announcement is to be sent to
            edsm (int or Null): the announcement parameter we want to run
                an EDSM system query on. none if Null.
            content (list of str): lines to be sent in the announcement
        """
        self.ID = ID
        self.name = name
        self.description = description
        self.channels = channels
        self._edsm = edsm
        self._content = ''.join(content)

    async def format(self, args) -> str:
        """Format announcement in a ready-to-be-sent format

        This includes the result of the EDSM query if specified in the config

        Args:
            *args: List of parameters to be formatted into the announcement

        Returns:
            (str): Fully formatted announcement

        Raises:
            IndexError: an invalid number of parameters was provided

        """
        if args["System"]:
            args["System"] = " ".join(args["System"].split())
        # Come on pylint
        try:
            announcement = self._content.format(**args)
        except IndexError:
            raise
        if self._edsm:
            try:
                announcement += await self.get_edsm_data(args)
            except ValueError:
                announcement += 'Attention Dispatch, please confirm clients system before proceeding.'
        return announcement

    async def get_edsm_data(self, args: Dict, twitter: bool = False) -> Optional[str]:
        """Calculates and formats a ready-to-go string with EDSM info about a system

        Args:
            args: Arguments for the case announcement
            twitter: True if the information is meant to be sent over Twitter, else False.

        Returns:
            (str) string with information about the existence of a system, plus
                distance and cardinal direction from the nearest landmark

        Raises:
            ValueError: Raised if System parameter is not present in `args` dict

        """
        if self._edsm and args["System"]:
            try:
                sys_name = args["System"]
                sys_regex = re.search(r"^[\w\s]+\s[A-z]{2}-[A-z]\s[A-z]\d+(-\d+)?", sys_name)
                if sys_regex:
                    # Search EDSM for the regex extracted proc-gen system name, if one was found
                    # This is an attempt to reduce the EDSM requests if a proc-gen system with body info is submitted by a client
                    sys_name = sys_regex.group(0)

                # Is meant to be but isn't procgen
                if "-" in sys_name and sys_regex is None:
                    sys_name_list = sys_name.split()
                    sys_name = ""
                    for index, block in enumerate(sys_name_list):
                        sys_name += block+" "
                        if "-" in block:
                            sys_name += sys_name_list[index+1]
                            break

                    sys_name = mistaken_char_subs(sys_name)
                    logger.debug(f"System name was char subbed from {args['System']} to {sys_name}")

                landmark, distance, direction = await checklandmarks(sys_name)
                exact_sys = sys_name == args["System"]

                # What we have is good, however, to make things look nice we need to flip the direction Drebin Style
                direction = cardinal_flip[direction]
                if twitter:
                    return f"{distance} LY {direction} of {landmark}"
                else:
                    if exact_sys:
                        return f"\nSystem exists in EDSM, {distance} LY {direction} of {landmark}."
                    else:
                        return f"\n{args['System']} could not be found in EDSM. System closest in name found in EDSM was"\
                               f" {sys_name}\n{sys_name} is {distance} LY {direction} of {landmark}. "
            except NoResultsEDSM as er:
                if str(er) == f"No major landmark systems within 10,000 ly of {args['System']}.":
                    dssa, distance, direction = await checkdssa(args['System'])
                    return f"\n{er}\nThe closest DSSA Carrier is in {dssa}, {distance} LY {direction} of " \
                           f"{args['System']}."
                else:
                    found_sys, close_sys = await get_nearby_system(sys_name)

                    if found_sys:
                        try:
                            landmark, distance, direction = await checklandmarks(close_sys)
                            return f"\n{args['System']} could not be found in EDSM. System closest in name found in EDSM was"\
                                   f" {close_sys}\n{close_sys} is {distance} LY {direction} of {landmark}. "
                        except NoResultsEDSM as er:
                            if str(er) == f"No major landmark systems within 10,000 ly of {close_sys}.":
                                dssa, distance, direction = await checkdssa(close_sys)
                                return f"\n{sys_name} could not be found in EDSM. System closest in name found in " \
                                       f"EDSM was {close_sys}.\n{er}\nThe closest DSSA Carrier is in " \
                                       f"{dssa}, {distance} LY {direction} of {close_sys}. "
                    else:
                        return "\nDistance to landmark or DSSA unknown." if twitter else "\nSystem Not Found in EDSM." \
                                                                                         " match to sys name format " \
                                                                                         "or sys name lookup " \
                                                                                         "failed.\nPlease check " \
                                                                                         "system name with client "

            except EDSMLookupError:
                return '' if twitter else "\nUnable to query EDSM."
        else:
            raise ValueError("Built-in EDSM lookup requires a 'System' parameter in the announcement configuration")
