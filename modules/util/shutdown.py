import os
import signal
import logging

import main
from typing import List

from ..checks import require_permission, DeniedMessage


@require_permission("ADMIN", message=DeniedMessage.ADMIN)
async def shutdown(bot: main, channel: str, sender: str, args: List[str], messagemode: int):
    logging.info("Shutdown has been ordered by {0}".format(sender))
    os.kill(os.getpid(), signal.SIGUSR2)
