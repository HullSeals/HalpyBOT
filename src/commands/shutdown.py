"""
HalpyBOT v1.5

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

from ..packages.checks import Require, Admin
from ..packages.command import Commands
from ..packages.models import Context
from ..packages.database import Grafana

logger = logging.getLogger(__name__)
logger.addHandler(Grafana)

@Commands.command("shutdown", "restart", "sealpukku")
@Require.DM()
@Require.permission(Admin)
async def cmd_shutdown(ctx: Context, args: List[str]):
    """
    Shut down the bot (restart if running as daemon)

    Usage: !shutdown
    Aliases: !reboot
    """
    logger.critical(f"Shutdown has been ordered by {ctx.sender}")
    await ctx.bot.quit(f"HalpyBOT restart ordered by {ctx.sender}. Stand By.")
    os.kill(os.getpid(), signal.SIGTERM)
