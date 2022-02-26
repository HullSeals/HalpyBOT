"""
HalpyBOT v1.5.2

twitter.py - Send case announcements over

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

"""

from ..configmanager import config
from ..database import Grafana

import tweepy
import logging

logger = logging.getLogger(__name__)
logger.addHandler(Grafana)


class TweetError(Exception):
    """
    Twitter module exception base class
    """


class TwitterNotEnabled(TweetError):
    """
    Could not announce over twitter because functionality has been disabled
    """


class TwitterConnectionError(TweetError):
    """
    Unable to execute twitter-related action because of a connection error
    """


class Twitter(tweepy.Client):

    def __init__(self, *args, **kwargs):
        if not config.getboolean('Twitter', 'enabled'):
            self._open = False
            return
        self._open = True
        super().__init__(*args, **kwargs)

    def __bool__(self):
        """Checks if Twitter functionality has been enabled in config

        Returns:
            (bool): True if enabled, False if not.

        """
        return self._open

    async def tweet_case(self, announcement, args):
        """Tweet a case

        Args:
            announcement (Announcement): Announcable object for the request
            args (dict): Announcement arguments dictionary

        Returns:
            Nothing

        """
        mainline_tw = f"A new {args['Platform']} case has come in."
        if self.__bool__():  # Eh, this is stupid and unneccesary I guess. Keep it anyway
            try:

                edsm_info = await announcement.get_edsm_data(args, twitter=True)
                twitmsg = f"{mainline_tw} {edsm_info} Call your jumps, Seals!"
                auth = tweepy.Client(consumer_key=config['Twitter']['api_key'],
                                     consumer_secret=config['Twitter']['api_secret'],
                                     access_token=config['Twitter']['access_token'],
                                     access_token_secret=config['Twitter']['access_secret'])
                auth.create_tweet(text=twitmsg)
            except (NameError, tweepy.errors.TweepyException) as err:
                logger.error(f"ERROR in Twitter Update: {err}")
                raise TwitterConnectionError(err)
        else:
            return


TwitterCasesAcc = Twitter(wait_on_rate_limit=True)
