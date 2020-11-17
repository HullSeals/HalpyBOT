"""
HalpyBOT v1.5

shutdown.py - Will be with you shortly, please hold!

Copyright (c) 2020 The Hull Seals,
All rights reserved

Licensed under the GNU General Public License
See license.md
"""


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
