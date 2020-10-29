from .checks import require_permission, Levels, deniedMessage
import main
from typing import List
from .datamodels.user import User

@require_permission(level=Levels.ADMIN, message=deniedMessage.ADMIN)
async def test(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    await bot.message(channel, "Test failed successfully")
    await bot.message(sender, f"Test failed successfully. Args:{args} Msgmode: {messagemode}")


#foo = await User.from_pydle(bot, nickname=sender)
#bar = User.process_vhost(foo.hostname)