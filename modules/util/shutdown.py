import os
import signal
import logging

import main
from typing import List

from modules.util.checks import require_permission, DeniedMessage, require_dm

@require_dm()
@require_permission("ADMIN", message=DeniedMessage.ADMIN)
async def shutdown(bot: main, channel: str, sender: str, in_channel: bool, args: List[str]):
    logging.info("Shutdown has been ordered by {0}".format(sender))
    os.kill(os.getpid(), signal.SIGUSR2)
