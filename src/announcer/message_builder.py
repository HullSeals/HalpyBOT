"""
HalpyBOT v1.5

message_builder.py - Build the messages for the announcer

Copyright (c) 2020 The Hull Seals,
All rights reserved

Licensed under the GNU General Public License
See license.md
"""


from typing import List

send_to = ["#Repair-Requests", "#Code-Black", "#seal-bob"]

async def codeblack(ctx, args: List[str]):
    message = f"xxxx CBCASE xxxx \n" \
              f"CMDR: {args[0]} -- Platform: {args[1]} System: {args[2]} -- Hull: {args[3]} \n" \
              f"Can synth: {args[4]} -- O2 timer: {args[5]} \n" \
              f"xxxx NEWCASE xxxx"
    for ch in send_to:
        await ctx.bot.message(ch, message)

async def pc(ctx, args: List[str]):
    message = f"xxxx PCCASE xxxx \n" \
              f"CMDR: {args[0]} -- Platform: {args[1]} \n" \
              f"System: {args[2]} -- Hull: {args[3]} \n" \
              f"xxxx NEWCASE xxxx"
    for ch in send_to:
        await ctx.bot.message(ch, message)

async def xb(ctx, args: List[str]):
    message = f"xxxx XBCASE xxxx \n" \
              f"CMDR: {args[0]} -- Platform: {args[1]} \n" \
              f"System: {args[2]} -- Hull: {args[3]} \n" \
              f"xxxx NEWCASE xxxx"
    for ch in send_to:
        await ctx.bot.message(ch, message)

async def ps(ctx, args: List[str]):
    message = f"xxxx PSCASE xxxx \n" \
              f"CMDR: {args[0]} -- Platform: {args[1]} \n" \
              f"System: {args[2]} -- Hull: {args[3]} \n" \
              f"xxxx NEWCASE xxxx"
    for ch in send_to:
        await ctx.bot.message(ch, message)

async def plterr(ctx, args: List[str]):
    message = f"xxxx PLATFORM_ERROR xxxx \n" \
              f"CMDR: {args[0]} -- Platform: {args[1]} \n" \
              f"System: {args[2]} -- Hull: {args[3]} \n" \
              f"xxxx NEWCASE xxxx"
    for ch in send_to:
        await ctx.bot.message(ch, message)

async def kingfisher_xb(ctx, args: List[str]):
    message = f"xxxx XBKFCASE xxxx\n" \
              f"CMDR: {args[0]} -- Platform: {args[1]}\n" \
              f"System: {args[2]} -- Planet: {args[3]}\n" \
              f"Coordinates: {args[4]}\n" \
              f"Type: {args[5]}\n" \
              f"xxxx NEWCASE xxxx"
    for ch in send_to:
        await ctx.bot.message(ch, message)

async def kingfisher_pc(ctx, args: List[str]):
    message = f"xxxx PCKFCASE xxxx\n" \
              f"CMDR: {args[0]} -- Platform: {args[1]}\n" \
              f"System: {args[2]} -- Planet: {args[3]}\n" \
              f"Coordinates: {args[4]}\n" \
              f"Type: {args[5]}\n" \
              f"xxxx NEWCASE xxxx"
    for ch in send_to:
        await ctx.bot.message(ch, message)

async def kingfisher_ps(ctx, args: List[str]):
    message = f"xxxx PSKFCASE xxxx\n" \
              f"CMDR: {args[0]} -- Platform: {args[1]}\n" \
              f"System: {args[2]} -- Planet: {args[3]}\n" \
              f"Coordinates: {args[4]}\n" \
              f"Type: {args[5]}\n" \
              f"xxxx NEWCASE xxxx"
    for ch in send_to:
        await ctx.bot.message(ch, message)

async def kingfisher_plterr(ctx, args: List[str]):
    message = f"xxxx PLATFORM_ERROR xxxx\n" \
              f"CMDR: {args[0]} -- Platform: {args[1]}\n" \
              f"System: {args[2]} -- Planet: {args[3]}\n" \
              f"Coordinates: {args[4]}\n" \
              f"Type: {args[5]}\n" \
              f"xxxx NEWCASE xxxx"
    for ch in send_to:
        await ctx.bot.message(ch, message)
