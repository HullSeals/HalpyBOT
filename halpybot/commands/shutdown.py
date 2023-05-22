"""
shutdown.py - Will be with you shortly, please hold!

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""


import os
import signal
from typing import List
from loguru import logger
from ..packages.checks import in_direct_message, needs_permission, Admin
from ..packages.command import Commands
from ..packages.models import Context


@Commands.command("shutdown", "restart", "sealpukku", "reboot")
@in_direct_message()
@needs_permission(Admin)
async def cmd_shutdown(ctx: Context, args: List[str]):
    """
    Shut down the bot (restart if running as daemon)

    Usage: !shutdown
    Aliases: !reboot
    """
    logger.critical("Shutdown has been ordered by {sender}", sender=ctx.sender)
    if len(args) == 0:
        await ctx.bot.quit(f"HalpyBOT restart ordered by {ctx.sender}. Stand By.")
    else:
        args = " ".join(args)
        await ctx.bot.quit(f"HalpyBOT restart ordered by {ctx.sender}. ({args})")
    os.kill(os.getpid(), signal.SIGTERM)
