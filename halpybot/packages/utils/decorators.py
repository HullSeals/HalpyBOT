"""
decorators.py - All of the various utility decorators in use for the Seals

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
import functools
from typing import List
from loguru import logger
from halpybot.packages.case import get_case
from halpybot.packages.command import get_help_text
from halpybot.packages.models import Case
from ..exceptions import (
    EDSMReturnError,
    NoResultsEDSM,
    EDSMLookupError,
    EDSMConnectionError,
)
from .utils import cache_prep, sys_cleaner


def sys_exceptions(function):
    """Handle the various possible EDSM Exceptions for system calculations"""

    @functools.wraps(function)
    async def guarded(ctx, args: List[str]):
        system, cache_override = await cache_prep(ctx, args)
        cleaned_sys = await sys_cleaner(system)
        try:
            return await function(ctx, cleaned_sys, cache_override)
        except NoResultsEDSM:
            return await ctx.reply(
                f"No system and/or commander named {system} was found in the EDSM database."
            )
        except EDSMReturnError:
            logger.exception("Received a malformed reply from EDSM.")
            return await ctx.reply(
                f"Received a reply from EDSM about {system}, but could not process the return."
            )
        except EDSMLookupError:
            logger.exception("Failed to query EDSM for coordinate details.")
            return await ctx.reply("Failed to query EDSM for coordinate details.")

    return guarded


def cmdr_exceptions(function):
    """Handle the various possible EDSM Exceptions for CMDR calculations"""

    @functools.wraps(function)
    async def guarded(ctx, args: List[str]):
        cmdr, cache_override = await cache_prep(ctx, args)
        try:
            return await function(ctx, cmdr, cache_override)
        except NoResultsEDSM:
            return await ctx.reply(
                f"No CMDR named {cmdr} was found in the EDSM database."
            )
        except EDSMReturnError:
            logger.exception("Received malformed reply from EDSM.")
            return await ctx.reply(
                f"Received a reply from EDSM about {cmdr}, but could not process the return."
            )
        except EDSMConnectionError:
            logger.exception("Failed to query EDSM for commander data.")
            return await ctx.reply("Failed to query EDSM for commander data.")

    return guarded


def coords_exceptions(function):
    """Handle the various possible EDSM Exceptions for coordinate calculations"""

    @functools.wraps(function)
    async def guarded(ctx, args: List[str]):
        if len(args) <= 2:  # Minimum Number of Args is 3.
            return await ctx.reply(get_help_text(ctx.bot.commandsfile, ctx.command))
        xcoord = args[0].strip()
        ycoord = args[1].strip()
        zcoord = args[2].strip()
        try:
            float(xcoord)
            float(ycoord)
            float(zcoord)
        except ValueError:
            return await ctx.reply("All coordinates must be numeric.")
        try:
            return await function(ctx, xcoord, ycoord, zcoord)
        except NoResultsEDSM:
            return await ctx.reply(
                "No system was found in the EDSM database for the given coordinates."
            )
        except EDSMReturnError:
            logger.exception("Received a malformed reply from EDSM.")
            return await ctx.reply(
                "Received a reply from EDSM about the given coordinates, "
                "but could not process the return."
            )
        except EDSMLookupError:
            logger.exception("Failed to query EDSM for coordinate details.")
            return await ctx.reply("Failed to query EDSM for coordinate details.")

    return guarded


def dist_exceptions(function):
    """Handle the various possible EDSM Exceptions for Distance calculations"""

    @functools.wraps(function)
    async def guarded(ctx, args: List[str]):
        if len(args) < 1:  # Minimum Number of Args is 2.
            return await ctx.reply(get_help_text(ctx.bot.commandsfile, ctx.command))
        cache_override = False
        if args[0] == "--new":
            cache_override = True
            del args[0]
            if not args:
                return await ctx.reply(get_help_text(ctx.bot.commandsfile, ctx.command))
        try:
            return await function(ctx, args, cache_override)
        except NoResultsEDSM:
            return await ctx.reply(
                "No system and/or commander was found in the EDSM database "
                "for one of the points."
            )
        except EDSMReturnError:
            logger.exception("Received a malformed reply from EDSM.")
            return await ctx.reply(
                "Received a reply from EDSM, but could not process the return."
            )
        except EDSMLookupError:
            logger.exception("Failed to query EDSM for system or CMDR details.")
            return await ctx.reply("Failed to query EDSM for system or CMDR details.")

    return guarded


def gather_case(len_args_expected: int):
    """Process gathering Case details for a command expecting a number of args"""

    def decorator(function):
        @functools.wraps(function)
        async def guarded(ctx, args: List[str]):
            if len(args) < len_args_expected:
                return await ctx.reply(get_help_text(ctx.bot.commandsfile, ctx.command))
            try:
                case: Case = await get_case(ctx, args[0])
            except KeyError:
                return await ctx.reply(f"No case found for {args[0]!r}.")
            return await function(ctx=ctx, args=args, case=case)

        return guarded

    return decorator
