"""
HalpyBOT v1.4

manual_case.py - Manual case creation module

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import List

from ..packages.command import Commands
from ..packages.checks import Require, Cyberseal
from ..packages.models import Context
from ..packages.announcer import Announcer

@Commands.command("testann")
@Require.permission(Cyberseal, message="This is here as a temporary test, don't touch it!")
async def cmd_testann(ctx: Context, args: List[str]):
    ann = Announcer(ctx.bot)
    await ann.announce(announcement='PPWK', args=['Rik079', 'Rixxan'])
