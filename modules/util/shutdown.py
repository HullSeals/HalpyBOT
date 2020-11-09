import os
import signal
import logging

from typing import List

from modules.util.checks import require_permission, DeniedMessage, require_dm

@require_dm()
@require_permission("ADMIN", message=DeniedMessage.ADMIN)
async def shutdown(ctx, args: List[str]):
    logging.info("Shutdown has been ordered by {0}".format(ctx.sender))
    os.kill(os.getpid(), signal.SIGUSR2)
