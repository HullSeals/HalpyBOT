import functools
from enum import Enum
import main
from typing import List
from .datamodels.user import User
import pydle

levels = {
    "rixxan.admin.hullseals.space": 7,
    "cybersealmgr.hullseals.space": 6,
    "cyberseal.hullseals.space": 5,
    "admin.hullseals.space": 4,
    "moderator.hullseals.space": 3,
    "seal.hullseals.space": 2,
    "pup.hullseals.space": 1,
    None: 0
}

# TODO copyright notice

class Levels(Enum):
    OWNER = 5
    CYBERMGR = 4
    ADMIN = 3
    MODERATOR = 2
    SEAL = 1
    NONE = 0

class deniedMessage:
    GENERIC = "Access denied.",
    DRILLED = "You have to be a drilled seal to use this!"
    MODERATOR = "Only moderators+ can use this."
    ADMIN = "Denied! This is for your friendly neighbourhood admin and cyberseal"
    CYBERMGR = "You need to be a cyberseal manager for this."
    OWNER = "You need to be a Rixxan to use this"


def require_permission(level: Levels, above: bool = True, message: str = None):

    def actual_decorator(function):
        @functools.wraps(function)
        async def guarded(bot: main, channel: str, nick: str, args: List[str], messagemode: int):
            # Set userLevel to 0 by default
            userlevel: Levels = Levels.NONE
            # Get role
            foo = await User.from_pydle(bot, nickname=nick)
            modes = User.process_vhost(foo.hostname)
            # Find user level
            userlevel = levels[modes]
            print(userlevel)
            # Convert required permission to level

            # If permission is not correct, send deniedMessage
            print("Test if block starts")
            if userlevel < level:
                print("Test_failed_perms")
                if message:
                    await bot.message(channel, message)
                    pass
            else:
                print("Test_passed")
                return await function(bot, channel, nick, args, messagemode)

        return guarded

    return actual_decorator
