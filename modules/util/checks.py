import functools
import main
from typing import List
from modules.datamodels.user import User

levels = {
    "Rixxan.admin.hullseals.space": 7,
    "cybersealmgr.hullseals.space": 6,
    "cyberseal.hullseals.space": 5,
    "admin.hullseals.space": 4,
    "moderator.hullseals.space": 3,
    "seal.hullseals.space": 2,
    "pup.hullseals.space": 1,
    None: 0
}


requiredlevel = {
    "OWNER": '7',
    "CYBERMGR": '6',
    "CYBER": '5',
    "ADMIN": '4',
    "MODERATOR": '3',
    "DRILLED": '2',
    "PUP": '1',
    "NONE": '0',
}

class DeniedMessage:
    GENERIC = "Access denied.",
    PUP = "You need to be registered and logged in with NickServ to use this"
    DRILLED = "You have to be a drilled seal to use this!"
    MODERATOR = "Only moderators+ can use this."
    ADMIN = "Denied! This is for your friendly neighbourhood admin"
    CYBER = "This can only be used by cyberseals."
    CYBERMGR = "You need to be a cyberseal manager for this."
    OWNER = "You need to be a Rixxan to use this"


def require_permission(req_level: str, above: bool = True, message: str = "Access Denied."):

    def decorator(function):
        @functools.wraps(function)
        async def guarded(bot: main, channel: str, nick: str, args: List[str], in_channel: bool):
            # Get role
            whois = await User.get_info(bot, nickname=nick)
            modes = User.process_vhost(whois.hostname)
            # Find user level
            userlevel = int(levels[modes])
            # Convert required permission to level
            level = int(requiredlevel[req_level])
            # If permission is not correct, send deniedMessage
            if userlevel < level:
                if in_channel is False:
                    await bot.message(nick, message)
                    pass
            else:
                return await function(bot, channel, nick, args, in_channel)

        return guarded

    return decorator


def require_dm():

    def decorator(function):
        @functools.wraps(function)
        async def guarded(bot: main, channel: str, nick: str, args: List[str], in_channel: bool):
            if in_channel:
                return
            else:
                return await function(bot, channel, nick, args, in_channel)

        return guarded

    return decorator


def require_channel():

    def decorator(function):
        @functools.wraps(function)
        async def guarded(bot: main, channel: str, nick: str, args: List[str], in_channel: bool):
            if in_channel is False:
                return
            else:
                return await function(bot, channel, nick, args, in_channel)

        return guarded

    return decorator