import os
import signal
import logging

from typing import List

from modules.util.checks import require_permission, DeniedMessage, require_dm

@require_dm()
@require_permission("ADMIN", message=DeniedMessage.ADMIN)
async def cmd_shutdown(ctx, args: List[str]):
    """
    Shut down the bot (restart if running as daemon)

    Usage: !shutdown
    Aliases: n/a
    """
    logging.info("Shutdown has been ordered by {0}".format(ctx.sender))
    os.kill(os.getpid(), signal.SIGUSR2)
