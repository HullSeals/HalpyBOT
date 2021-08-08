"""
HalpyBOT v1.4

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
import logging
import tweepy

from ..configmanager import config

from ..edsm import checklandmarks, NoResultsEDSM, EDSMLookupError

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
        ann = self._announcements[announcement]
        # noinspection PyBroadException
        # We want to catch everything
        global twita
        twita = "empty"
        if "Platform" in args:
            twita = f"A new {args['Platform']} case has come in."
        try:
            for ch in ann.channels:
                await self._client.message(ch, await ann.format(args))
        except Exception as ex:
            raise AnnouncementError(ex)

class Announcement:

    def __init__(self, ID: str, name: str, description: str,
                 channels: List[str], edsm: Optional[int], content: List[str]):
        """Create a new announcement object

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
        edsmstr = ''
        try:
            announcement = self._content.format(**args)
        except IndexError:
            raise
        if self._edsm and args["System"]:
            try:
                landmark, distance, direction = await checklandmarks(args["System"])
                # What we have is good, however, to make things look nice we need to flip the direction Aussie Style
                dirA = ["North", "NE", "East", "SE", "South", "SW", "West", "NW", "North"]
                olddir = dirA.index(direction)
                dirB = ["South", "SW", "West", "NW", "North", "NE", "East", "SE", "South"]
                direction = f'{dirB[olddir]}'
                edsmstr = f"\nSystem exists in EDSM, {distance} LY {direction} of {landmark}."
                classtype = 1
            except NoResultsEDSM:
                edsmstr = f"\nSystem {args['System']} not found in EDSM."
                classtype = 2
            except EDSMLookupError:
                edsmstr = f"\nUnable to query EDSM. Dispatch, please contact a cyberseal."
                classtype = 3
        elif self._edsm:
            ValueError("Built-in EDSM lookup requires a 'System' parameter in the announcement configuration")
        if twita != "empty":
            try:
                if classtype == 1:
                    twitstr = edsmstr.strip()
                else:
                    twitstr = "System Not Found in EDSM."
                twitmsg = f"{twita} {twitstr} Call your jumps, Seals!"
                auth = tweepy.OAuthHandler(config['Twitter']['api_key'],
                                           config['Twitter']['api_secret'])
                auth.set_access_token(config['Twitter']['access_token'],
                                      config['Twitter']['access_secret'])
                api = tweepy.API(auth, wait_on_rate_limit=True,
                                 wait_on_rate_limit_notify=True)
                try:
                    api.verify_credentials()
                except tweepy.error.TweepError as err:
                    logging.error(f"ERROR in Twitter Authentication: {err}")
                #api.update_status(twitmsg)
            except NameError:
                pass
        del globals()['twita']
        return announcement + edsmstr
