"""
announcer.py - Client announcement handler

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

"""

import json
from typing import List, Dict, Optional
from attrs import define
from ..edsm import (
    checklandmarks,
    get_nearby_system,
    NoResultsEDSM,
    EDSMLookupError,
    checkdssa,
    sys_cleaner,
    NoNearbyEDSM,
)

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


async def get_edsm_data(args: Dict, generalized: bool = False) -> Optional[str]:
    """Calculates and formats a ready-to-go string with EDSM info about a system

    Args:
        args: Arguments for the case announcement
        generalized: True if the information is meant to be vague, else False.

    Returns:
        (str) string with information about the existence of a system, plus
            distance and cardinal direction from the nearest landmark

    Raises:
        ValueError: Raised if System parameter is not present in `args` dict

    """
    if "System" not in args:
        raise ValueError(
            "Built-in EDSM lookup requires a 'System' parameter in the announcement configuration"
        )
    sys_name = args["System"]
    try:
        landmark, distance, direction = await checklandmarks(sys_name)
        # What we have is good, however, to make things look nice we need to flip the direction Drebin Style
        direction = cardinal_flip[direction]
        if generalized:
            return (
                f"{distance} LY {direction} of {landmark}"
                if generalized
                else f"\nSystem exists in EDSM, {distance} LY {direction} of {landmark}."
            )
    except NoNearbyEDSM:
        dssa, distance, direction = await checkdssa(sys_name)
        return (
            "No major landmark found within 10,000 LY of the provided system."
            if generalized
            else f"\nNo major landmark found within 10,000 LY of {sys_name}."
            f"\nThe closest DSSA Carrier is in {dssa}, {distance} LY {direction} of {sys_name}."
        )
    except NoResultsEDSM:
        found_sys, close_sys = await get_nearby_system(sys_name)
        if found_sys:
            try:
                landmark, distance, direction = await checklandmarks(close_sys)
                return (
                    f"System Cleaner found a matching EDSM system {distance} LY {direction} of "
                    f"{landmark}."
                    if generalized
                    else f"\n{sys_name} could not be found in EDSM. "
                    f"System closest in name found in "
                    f"EDSM was {close_sys}\n{close_sys} is {distance} LY {direction} of {landmark}. "
                )
            except NoNearbyEDSM:
                dssa, distance, direction = await checkdssa(close_sys)
                return (
                    f"Corrected system calculated to be {distance} LY {direction} of {dssa}."
                    if generalized
                    else f"\nThe closest DSSA Carrier is "
                    f"in {dssa}, {distance} LY {direction} of {close_sys}. "
                )
        return (
            "\nDistance to landmark or DSSA unknown. Check case details with Dispatch."
            if generalized
            else "\nSystem Not Found in EDSM.\n" "Please check system name with client."
        )
    except EDSMLookupError:
        return "\nUnable to query EDSM."


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
        except Exception as announcement_exception:
            raise AnnouncementError(Exception) from announcement_exception


@define
class Announcement:
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

    ann_type: str
    name: str
    description: str
    channels: List[str]
    content: List[str]
    edsm: Optional[int] = None

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
        formatted_content = "".join(self.content)
        announcement = formatted_content.format(**args)
        if self.edsm:
            try:
                announcement += await get_edsm_data(args)
            except ValueError:
                announcement += "\nAttention Dispatch, please confirm clients system before proceeding."
        return announcement
