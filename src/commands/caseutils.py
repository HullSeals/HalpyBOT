"""
HalpyBOT v1.5

caseutils.py - Commands involving the management of Seal cases

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
from typing import List
from ..packages.command import Commands
from ..packages.facts import Facts
from ..packages.models import Context, User


@Commands.command("go")
async def cmd_go(ctx: Context, args: List[str]):
    """
    Check if an assigned Seal is trained and Identified before sending.

    Usage: !go [seals]
    Aliases: n/a
    """
    # If no args presented, skip the user check. This will be removed in later versions, args will be required.
    if args:
        # Clean out the list, only pass "full" args.
        args = [x.strip(' ') for x in args]
        args = [ele for ele in args if ele.strip()]
        # Loop through the list, checking each to see if they are actually a user.
        for seal in args:
            user_level = 1
            # AttributeError is thrown if a user does not exist. Accept and move on.
            try:
                whois = await User.get_info(ctx.bot, str(seal))
                vhost = User.process_vhost(whois.hostname)
            except AttributeError:
                vhost = 'notUser'
            # There is no hard set "not a seal" vhost level.
            if vhost is None:
                user_level = 0
            if user_level == 0:
                await ctx.reply(f"{ctx.sender}: {str(seal)} is not identified as a trained seal. Have them check their "
                                f"IRC setup?")

    return await ctx.reply(await Facts.fact_formatted(fact=('go', 'en'), arguments=args))
