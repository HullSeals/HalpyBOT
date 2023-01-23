"""
announcer.py - Client announcement handler

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

"""

import json
from typing import List, Dict, Optional
from loguru import logger
import tweepy
from ..edsm import (
    checklandmarks,
    get_nearby_system,
    NoResultsEDSM,
    EDSMLookupError,
    checkdssa,
    sys_cleaner,
    NoNearbyEDSM,
)
from ... import config

cardinal_flip = {
    "North": "South",
    "NE": "SW",
    "East": "West",
    "SE": "NW",
    "South": "North",
    "SW": "NE",
    "West": "East",
    "NW": "SE",
}


async def get_edsm_data(args: Dict, twitter: bool = False) -> Optional[str]:
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
    if args["System"]:
        sys_name = args["System"]
        try:
            exact_sys = sys_name == args["System"]
            landmark, distance, direction = await checklandmarks(sys_name)
            # What we have is good, however, to make things look nice we need to flip the direction Drebin Style
            direction = cardinal_flip[direction]
            if twitter:
                return f"{distance} LY {direction} of {landmark}"
            if exact_sys:
                return (
                    f"\nSystem exists in EDSM, {distance} LY {direction} of {landmark}."
                )
            return (
                f"Corrected system exists in EDSM, {distance} LY {direction} of {landmark}."
                if twitter
                else f"System cleaner found a matching EDSM system. {sys_name} is {distance} LY "
                f"{direction} of {landmark}."
            )
        except NoNearbyEDSM:
            dssa, distance, direction = await checkdssa(args["System"])
            return (
                "No major landmark found within 10,000 LY of the provided system."
                if twitter
                else f"\nNo major landmark found within 10,000 LY {args['System']}."
                f"\nThe closest DSSA Carrier is in {dssa}, {distance} LY {direction} of {args['System']}."
            )
        except NoResultsEDSM:
            found_sys, close_sys = await get_nearby_system(sys_name)
            if found_sys:
                try:
                    landmark, distance, direction = await checklandmarks(close_sys)
                    return (
                        f"System Cleaner found a matching EDSM system {distance} LY {direction} of "
                        f"{landmark}."
                        if twitter
                        else f"\n{args['System']} could not be found in EDSM. "
                        f"System closest in name found in "
                        f"EDSM was {close_sys}\n{close_sys} is {distance} LY {direction} of {landmark}. "
                    )
                except NoNearbyEDSM:
                    dssa, distance, direction = await checkdssa(close_sys)
                    return (
                        f"Corrected system calculated to be {distance} LY {direction} of {dssa}."
                        if twitter
                        else f"\nThe closest DSSA Carrier is "
                        f"in {dssa}, {distance} LY {direction} of {close_sys}. "
                    )
            return (
                "\nDistance to landmark or DSSA unknown. Check case details with Dispatch."
                if twitter
                else "\nSystem Not Found in EDSM.\n"
                "Please check system name with client."
            )
        except EDSMLookupError:
            return "" if twitter else "\nUnable to query EDSM."
    else:
        raise ValueError(
            "Built-in EDSM lookup requires a 'System' parameter in the announcement configuration"
        )


async def tweet_case(args):
    """Tweet a case

    Args:
        args (dict): Announcement arguments dictionary

    Returns:
        Nothing

    """
    mainline_tw = f"A new {args['Platform']} case has come in."
    try:
        edsm_info = await get_edsm_data(args, twitter=True)
        twitmsg = f"{mainline_tw} {edsm_info} Call your jumps, Seals!"
        auth = tweepy.Client(
            consumer_key=config.twitter.api_key.get_secret_value(),
            consumer_secret=config.twitter.api_secret.get_secret_value(),
            access_token=config.twitter.access_token,
            access_token_secret=config.twitter.access_secret.get_secret_value(),
        )
        auth.create_tweet(text=twitmsg)
    except (NameError, tweepy.errors.TweepyException):
        logger.exception("Unable to send case details to Twitter.")
        return


class AnnouncementError(Exception):
    """
    Could not announce request
    """


class Announcer:
    def __init__(self):
        """Initialize the Announcer"""
        self._announcements = {}
        # Load data
        # TODO(theunknown1): load dataclass
        with open(
            "data/announcer/announcer.json", "r", encoding="UTF-8"
        ) as announcer_json:
            self._config = json.load(announcer_json)
        # Create announcement objects and store them in dict
        for ann_type in self._config["AnnouncerType"]:
            self._announcements[ann_type["ID"]] = Announcement(
                ann_type=ann_type["ID"],
                name=ann_type["Name"],
                description=ann_type["Description"],
                channels=ann_type["Channels"],
                edsm=ann_type["EDSM"],
                content=ann_type["Content"],
            )

    async def announce(self, announcement: str, args: Dict, client):
        """Announce a new case

        Args:
            announcement: The type of announcement to make
            args: Arguments for the case announcement
            client: The IRC Bot instance, used to send messages.

        Returns:
            Nothing

        Raises:
            AnnouncementError: Case could not be announced for any reason

        """
        ann = self._announcements[announcement]
        # noinspection PyBroadException
        # We want to catch everything
        try:
            for channel in ann.channels:
                await client.message(channel, await ann.format(args))
            if "Platform" in args.keys():
                if config.twitter.enabled:
                    await tweet_case(args)
        except Exception as announcement_exception:
            raise AnnouncementError(Exception) from announcement_exception


class Announcement:
    def __init__(
        self,
        ann_type: str,
        name: str,
        description: str,
        channels: List[str],
        edsm: Optional[int],
        content: List[str],
    ):
        """Create a new announceable object

        Args:
            ann_type (str): Announcement reference code, used by API
            name (str): Name, for reference only
            description (str): Description of the announcement
            channels (list of str): channels the announcement is to be sent to
            edsm (int or Null): the announcement parameter we want to run
                an EDSM system query on. none if Null.
            content (list of str): lines to be sent in the announcement
        """
        self.ann_type = ann_type
        self.name = name
        self.description = description
        self.channels = channels
        self._edsm = edsm
        self._content = "".join(content)

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
        if "System" in args.keys():
            args["System"] = await sys_cleaner(args["System"])
        # Come on pylint
        announcement = self._content.format(**args)
        if self._edsm:
            try:
                announcement += await get_edsm_data(args)
            except ValueError:
                announcement += "\nAttention Dispatch, please confirm clients system before proceeding."
        return announcement
