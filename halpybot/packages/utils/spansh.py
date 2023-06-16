"""
spansh.py - Jump Count calculator

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
from typing import List
import aiohttp
import asyncio
from loguru import logger
from halpybot import config
from .utils import web_get
from ..exceptions import SpanshNoResponse, SpanshBadResponse, SpanshResponseTimedOut
from ..models import Context


async def spansh_get_routes(
    ctx: Context,
    range: str,
    sysa: str,
    sysb: str,
    sysa_text: str,
    sysb_text: str,
    normal_jobID: str,
    neutron_jobID: str,
) -> None:
    """
    Receives calculated Normal and Neutron Jump Counts from spansh.co.uk

    Args:
        ctx (Context): PYDLE Context
        range (str): Ship's jump range
        sysa (str): Starting system
        sysb (str): Client's/Target system
        normal_jobID (str): spansh jobID for 100% efficency route
        neutron_jobID (str): spansh jobID for 60% efficency route

    Returns:
        None

    Raises:
        SpanshNoResponse: spansh did not respond in time.
        SpanshBadResponse: Spansh returned an unprocessable response
        SpanshResponseTimedOut: Spansh took too long to calculate a route
    """
    results_uri = f"https://spansh.co.uk/api/results"
    page_uri = f"https://spansh.co.uk/plotter/results"
    spansh_loop = True
    spansh_loop_timeout = 20
    while spansh_loop:
        try:
            responses = await web_get(f"{results_uri}/{normal_jobID}")
        except aiohttp.ClientError as ex:
            logger.exception("spansh did not respond (3)")
            raise SpanshNoResponse from ex
        if responses["status"] == "ok":
            spansh_loop = False
            normal_jumps = 0
            for entry in responses["result"]["system_jumps"]:
                normal_jumps += entry["jumps"]
            print(f"{normal_jumps} normal jumps")
            break
        if spansh_loop_timeout <= 0:
            logger.exception("spansh took too long to calculate a route (1)")
            raise SpanshResponseTimedOut
        spansh_loop_timeout -= 1
        await asyncio.sleep(1)
    spansh_loop = True
    while spansh_loop:
        try:
            responses = await web_get(f"{results_uri}/{neutron_jobID}")
        except aiohttp.ClientError as ex:
            logger.exception("spansh did not respond (4)")
            raise SpanshNoResponse from ex
        if responses["status"] == "ok":
            spansh_loop = False
            neutron_jumps = 0
            for entry in responses["result"]["system_jumps"]:
                neutron_jumps += entry["jumps"]
            print(f"{neutron_jumps} neutron jumps")
            break
        if spansh_loop_timeout <= 0:
            logger.exception("spansh took too long to calculate a route (2)")
            raise SpanshResponseTimedOut
        spansh_loop_timeout -= 1
        await asyncio.sleep(1)
    await ctx.reply(
        f"{ctx.sender}: It will take about {normal_jumps} normal jumps or {neutron_jumps} spansh jumps to get from {sysa_text} to {sysb_text} with a range of {range}LY."
    )
    await ctx.reply(f"spansh URL: {page_uri}/{neutron_jobID}")


async def spansh(
    ctx: Context, range: str, sysa: str, sysb: str, sysa_text: str, sysb_text: str
):
    """
    Starts calculating the normal and Neutron Jump Count using spansh.co.uk

    Args:
        ctx (Context): PYDLE Context
        range (str): Ship's jump range
        sysa (str): Starting system
        sysb (str): Client's/Target system

    Returns:
        ctx.reply()

    Raises:
        SpanshNoResponse: spansh did not respond in time.
        SpanshBadResponse: Spansh returned an unprocessable response
    """
    route_uri = f"https://spansh.co.uk/api/route"
    params = {
        "efficiency": 100,
        "range": range,
        "from": sysa,
        "to": sysb,
    }
    try:
        responses = await web_get(route_uri, params)
    except aiohttp.ClientError as ex:
        logger.exception("spansh Did Not Respond (1)")
        raise SpanshNoResponse from ex
    if "error" in responses:
        return await ctx.reply(f"{responses['error']}")
    if "job" not in responses:
        raise SpanshBadResponse
    normal_jobID = responses["job"]
    print(normal_jobID)
    params["efficiency"] = 60
    try:
        responses = await web_get(route_uri, params)
    except aiohttp.ClientError as ex:
        logger.exception("spansh Did Not Respond (2)")
        raise SpanshNoResponse from ex
    if "error" in responses:
        return await ctx.reply(f"{responses['error']}")
    if "job" not in responses:
        raise SpanshBadResponse
    neutron_jobID = responses["job"]
    print(neutron_jobID)
    asyncio.create_task(
        spansh_get_routes(
            ctx, range, sysa, sysb, sysa_text, sysb_text, normal_jobID, neutron_jobID
        )
    )
    return await ctx.reply(f"Spansh calculations have been started...")
