"""
HalpyBOT v1.3.1

message_builder.py - Build the messages for the announcer

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from ..edsm import *
from typing import List
import main

def send_to(annmodule: str, type: str):
    return [entry.strip() for entry in main.config.get(annmodule, type).split(',')]


async def codeblack(ctx, args: List[str]):
    message = f"xxxx CBCASE -- NEWCASE xxxx \n" \
              f"CMDR: {args[0]} -- Platform: {args[1]} System: {args[2]} -- Hull: {args[3]} \n" \
              f"Can synth: {args[4]} -- O2 timer: {args[5]} \n" \
              f"xxxxxxxx"
    message2 = await casecheck(ctx, sys=args[2])
    for ch in send_to('Announcer.cases', 'channels'):
        await ctx.bot.message(ch, message)
        await ctx.bot.message(ch, message2)


async def case(ctx, args: List[str]):
    message = f"xxxx {args[1]}CASE -- NEWCASE xxxx \n" \
              f"CMDR: {args[0]} -- Platform: {args[1]} \n" \
              f"System: {args[2]} -- Hull: {args[3]} \n" \
              f"xxxxxxxx"
    message2 = await casecheck(ctx, sys=args[2])
    for ch in send_to('Announcer.cases', 'channels'):
        await ctx.bot.message(ch, message)
        await ctx.bot.message(ch, message2)


async def plterr(ctx, args: List[str]):
    message = f"xxxx PLATFORM_ERROR -- NEWCASE xxxx \n" \
              f"CMDR: {args[0]} -- Platform: {args[1]} \n" \
              f"System: {args[2]} -- Hull: {args[3]} \n" \
              f"xxxxxxxx"
    message2 = await casecheck(ctx, sys=args[2])
    for ch in send_to('Announcer.cases', 'channels'):
        await ctx.bot.message(ch, message)
        await ctx.bot.message(ch, message2)


async def kingfisher(ctx, args: List[str]):
    message = f"xxxx {args[1]}KFCASE -- NEWCASE xxxx\n" \
              f"CMDR: {args[0]} -- Platform: {args[1]}\n" \
              f"System: {args[2]} -- Planet: {args[3]}\n" \
              f"Coordinates: {args[4]}\n" \
              f"Type: {args[5]}\n" \
              f"xxxxxxxx"
    message2 = await casecheck(ctx, sys=args[2])
    for ch in send_to('Announcer.cases', 'channels'):
        await ctx.bot.message(ch, message)
        await ctx.bot.message(ch, message2)


async def kingfisher_plterr(ctx, args: List[str]):
    message = f"xxxx PLATFORM_ERROR -- NEWCASE xxxx\n" \
              f"CMDR: {args[0]} -- Platform: {args[1]}\n" \
              f"System: {args[2]} -- Planet: {args[3]}\n" \
              f"Coordinates: {args[4]}\n" \
              f"Type: {args[5]}\n" \
              f"xxxxxxxx"
    message2 = await casecheck(ctx, sys=args[2])
    for ch in send_to('Announcer.cases', 'channels'):
        await ctx.bot.message(ch, message)
        await ctx.bot.message(ch, message2)


async def ppwk(ctx, args: List[str]):
    for ch in send_to('Announcer.paperwork', 'channels'):
        await ctx.bot.message(ch, f"Paperwork for case {args[0]} completed by {args[1]}")


async def casecheck(ctx, sys):
    try:
        if await GalaxySystem.exists(name=sys, CacheOverride=False):
            try:
                landmark, distance = await checklandmarks(SysName=sys, CacheOverride=False)
                message2 = f"System exists in EDSM. The closest landmark system is {landmark} at {distance} LY."
            except NoResultsEDSM:
                message2 = f"System {sys} exists, but no landmark system nearby."
            except EDSMLookupError as er:
                message2 = str(er)
        else:
            message2 = f"System {sys} not found in EDSM"
    except EDSMLookupError as er:
            message2 = str(er)  # Return error if one is raised down the call stack.
    return message2
