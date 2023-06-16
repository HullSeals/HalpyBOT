"""
spansh.py - Jump Count calculator

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
from typing import List
import asyncio
import aiohttp
from loguru import logger
from . import shorten, web_get
from ..exceptions import SpanshNoResponse, SpanshBadResponse, SpanshResponseTimedOut
from ..models import Context


async def spansh_get_routes(
    ctx: Context, jump_range: float, sysa: str, sysb: str, jobs: List[str]
) -> None:
    """
    Receives calculated Normal and Neutron Jump Counts from spansh.co.uk

    Args:
        ctx (Context): PYDLE Context
        jump_range (str): Ship's jump range
        sysa (str): Starting system
        sysb (str): Client's/Target system
        jobs (list): A list of two Spansh processing jobs

    Returns:
        None

    Raises:
        SpanshNoResponse: spansh did not respond in time.
        SpanshBadResponse: Spansh returned an unprocessable response
        SpanshResponseTimedOut: Spansh took too long to calculate a route
    """
    results_uri = "https://spansh.co.uk/api/results"  # TODO: Config
    page_uri = "https://spansh.co.uk/plotter/results"  # TODO: Config
    spansh_loop_timeout = 20  # TODO: Config
    job_results = []
    for job in jobs:
        while True:
            try:
                responses = await web_get(f"{results_uri}/{job}")
            except aiohttp.ClientError as ex:
                logger.exception("spansh did not respond (3)")  # TODO: Cleanup
                raise SpanshNoResponse from ex
            if responses["status"] == "ok":
                jumps = 0
                for entry in responses["result"]["system_jumps"]:
                    jumps += entry["jumps"]
                job_results.append(jumps)
                break
            if spansh_loop_timeout <= 0:
                logger.exception("spansh took too long to calculate a route (1)")
                raise SpanshResponseTimedOut
            spansh_loop_timeout -= 1
            await asyncio.sleep(1)
    await ctx.reply(
        f"{ctx.sender}: It will take about {job_results[1]} normal jumps or {job_results[0]} spansh jumps to get from {sysa} to {sysb} with a range of {jump_range} LY."
    )
    sysa = sysa.replace(" ", "%20")
    sysb = sysb.replace(" ", "%20")
    short = await shorten(
        f"{page_uri}/{jobs[0]}?efficiency=60&from={sysa}&to={sysb}&range={jump_range}"
    )
    return await ctx.reply(f"Here's a spansh URL: {short}")


async def spansh(ctx: Context, jump_range: float, sysa: str, sysb: str):
    """
    Starts calculating the normal and Neutron Jump Count using spansh.co.uk

    Args:
        ctx (Context): PYDLE Context
        jump_range (str): Ship's jump range
        sysa (str): Starting system
        sysb (str): Client's/Target system

    Returns:
        ctx.reply()

    Raises:
        SpanshNoResponse: spansh did not respond in time.
        SpanshBadResponse: Spansh returned an unprocessable response
    """
    route_uri = "https://spansh.co.uk/api/route"  # TODO: Config File
    params = {
        "efficiency": 100,
        "range": jump_range,
        "from": sysa,
        "to": sysb,
    }
    try:
        responses = await web_get(route_uri, params)
    except aiohttp.ClientError as ex:
        logger.exception("spansh Did Not Respond (1)")
        raise SpanshNoResponse from ex
    if "error" in responses:
        return await ctx.reply(f"{responses['error']}")  # TODO: Obfuscate
    if "job" not in responses:
        raise SpanshBadResponse
    normal_job_id = responses["job"]
    params["efficiency"] = 60
    try:
        responses = await web_get(route_uri, params)
    except aiohttp.ClientError as ex:
        logger.exception("spansh Did Not Respond (2)")
        raise SpanshNoResponse from ex
    if "error" in responses:
        return await ctx.reply(f"{responses['error']}")  # TODO: Obfuscate
    if "job" not in responses:
        raise SpanshBadResponse
    neutron_job_id = responses["job"]
    jobs = [neutron_job_id, normal_job_id]
    asyncio.create_task(spansh_get_routes(ctx, jump_range, sysa, sysb, jobs))

    return await ctx.reply("Spansh calculations have been started...")
