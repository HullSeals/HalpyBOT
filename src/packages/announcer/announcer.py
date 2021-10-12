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
from typing import List, Dict, Optional

from ..edsm import checklandmarks, NoResultsEDSM, EDSMLookupError
from .twitter import TwitterCasesAcc, TwitterConnectionError

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
                landmark, distance, direction = await checklandmarks(args["System"])
                # What we have is good, however, to make things look nice we need to flip the direction Drebin Style
                direction = cardinal_flip[direction]
                if twitter:
                    return f"{distance} LY {direction} of {landmark}"
                else:
                    return f"\nSystem exists in EDSM, {distance} LY {direction} of {landmark}."
            except NoResultsEDSM:
                return "\nDistance to landmark unknown." if twitter else "\nSystem Not Found in EDSM."
            except EDSMLookupError:
                return '' if twitter else "\nUnable to query EDSM."
        else:
            raise ValueError("Built-in EDSM lookup requires a 'System' parameter in the announcement configuration")
