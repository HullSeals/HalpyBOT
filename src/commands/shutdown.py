"""
HalpyBOT v1.4

shutdown.py - Will be with you shortly, please hold!

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""


import os
import signal
import logging
from typing import List

from ..packages.checks import Require, DeniedMessage
from ..packages.command import Commands
from ..packages.models import Context

@Commands.command("shutdown")
@Require.DM()
@Require.permission("ADMIN", message=DeniedMessage.ADMIN)
async def cmd_shutdown(ctx: Context, args: List[str]):
    """
    Shut down the bot (restart if running as daemon)

    Usage: !shutdown
    Aliases: n/a
    """
    logging.critical(f"Shutdown has been ordered by {ctx.sender}")
    os.kill(os.getpid(), signal.SIGUSR2)
