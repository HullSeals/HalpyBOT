"""
HalpyBOT v1.5

message_builder.py - Build the messages for the announcer

Copyright (c) 2020 The Hull Seals,
All rights reserved

Licensed under the GNU General Public License
See license.md
"""


from typing import List

send_to = ["#Repair-Requests", "#seal-bob"]

async def codeblack(ctx, args: List[str]):
    message = f"xxxx CBCASE -- NEWCASE xxxx \n" \
              f"CMDR: {args[0]} -- Platform: {args[1]} System: {args[2]} -- Hull: {args[3]} \n" \
              f"Can synth: {args[4]} -- O2 timer: {args[5]} \n" \
              f"xxxxxxxx"
    for ch in send_to:
        await ctx.bot.message(ch, message)

async def pc(ctx, args: List[str]):
    message = f"xxxx PCCASE -- NEWCASE xxxx \n" \
              f"CMDR: {args[0]} -- Platform: {args[1]} \n" \
              f"System: {args[2]} -- Hull: {args[3]} \n" \
              f"xxxxxxxx"
    for ch in send_to:
        await ctx.bot.message(ch, message)

async def xb(ctx, args: List[str]):
    message = f"xxxx XBCASE -- NEWCASE xxxx \n" \
              f"CMDR: {args[0]} -- Platform: {args[1]} \n" \
              f"System: {args[2]} -- Hull: {args[3]} \n" \
              f"xxxxxxxx"
    for ch in send_to:
        await ctx.bot.message(ch, message)

async def ps(ctx, args: List[str]):
    message = f"xxxx PSCASE -- NEWCASE xxxx \n" \
              f"CMDR: {args[0]} -- Platform: {args[1]} \n" \
              f"System: {args[2]} -- Hull: {args[3]} \n" \
              f"xxxxxxxx"
    for ch in send_to:
        await ctx.bot.message(ch, message)

async def plterr(ctx, args: List[str]):
    message = f"xxxx PLATFORM_ERROR -- NEWCASE xxxx \n" \
              f"CMDR: {args[0]} -- Platform: {args[1]} \n" \
              f"System: {args[2]} -- Hull: {args[3]} \n" \
              f"xxxxxxxx"
    for ch in send_to:
        await ctx.bot.message(ch, message)

async def kingfisher_xb(ctx, args: List[str]):
    message = f"xxxx XBKFCASE -- NEWCASE xxxx\n" \
              f"CMDR: {args[0]} -- Platform: {args[1]}\n" \
              f"System: {args[2]} -- Planet: {args[3]}\n" \
              f"Coordinates: {args[4]}\n" \
              f"Type: {args[5]}\n" \
              f"xxxxxxxx"
    for ch in send_to:
        await ctx.bot.message(ch, message)

async def kingfisher_pc(ctx, args: List[str]):
    message = f"xxxx PCKFCASE -- NEWCASE xxxx\n" \
              f"CMDR: {args[0]} -- Platform: {args[1]}\n" \
              f"System: {args[2]} -- Planet: {args[3]}\n" \
              f"Coordinates: {args[4]}\n" \
              f"Type: {args[5]}\n" \
              f"xxxxxxxx"
    for ch in send_to:
        await ctx.bot.message(ch, message)

async def kingfisher_ps(ctx, args: List[str]):
    message = f"xxxx PSKFCASE -- NEWCASE xxxx\n" \
              f"CMDR: {args[0]} -- Platform: {args[1]}\n" \
              f"System: {args[2]} -- Planet: {args[3]}\n" \
              f"Coordinates: {args[4]}\n" \
              f"Type: {args[5]}\n" \
              f"xxxxxxxx"
    for ch in send_to:
        await ctx.bot.message(ch, message)

async def kingfisher_plterr(ctx, args: List[str]):
    message = f"xxxx PLATFORM_ERROR -- NEWCASE xxxx\n" \
              f"CMDR: {args[0]} -- Platform: {args[1]}\n" \
              f"System: {args[2]} -- Planet: {args[3]}\n" \
              f"Coordinates: {args[4]}\n" \
              f"Type: {args[5]}\n" \
              f"xxxxxxxx"
    for ch in send_to:
        await ctx.bot.message(ch, message)

async def ppwk(ctx, args: List[str]):
    message = f"Paperwork for case {args[1]} completed by {args[2]}!"
    for ch in send_to:
        await ctx.bot.message(ch, message)
