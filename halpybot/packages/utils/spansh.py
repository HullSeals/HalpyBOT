"""
spansh.py - Your GPS for the Neutron Highway!

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
from typing import List
import asyncio
import aiohttp
from loguru import logger
from halpybot import config
from . import shorten, web_get
from ..exceptions import SpanshNoResponse, SpanshBadResponse, SpanshResponseTimedOut
from ..models import Context


async def spansh_get_routes(
    ctx: Context,
    jump_range: float,
    sysa: str,
    sysb: str,
    pointa_pretty: str,
    pointb_pretty: str,
    jobs: List[str],
) -> None:
    """
    Receives calculated Normal and Neutron Jump Counts from spansh.co.uk

    Args:
        ctx (Context): PYDLE Context
        jump_range (str): Ship's jump range
        sysa (str): Starting system
        sysb (str): Client's/Target system
        pointa_pretty (str): Starting system pre-formatted
        pointb_pretty (str): Client's/Target system pre-formatted
        jobs (list): A list of two Spansh processing jobs

    Returns:
        None

    Raises:
        SpanshNoResponse: spansh did not respond in time.
        SpanshBadResponse: Spansh returned an unprocessable response
        SpanshResponseTimedOut: Spansh took too long to calculate a route

        Unable to find route
    """
    spansh_loop_timeout = config.spansh.calculations_timeout
    job_results = []
    for job in jobs:
        while True:
            try:
                responses = await web_get(f"{config.spansh.results_uri}/{job}")
            except aiohttp.ClientError as ex:
                logger.exception(
                    "spansh did not respond while trying to receive the calculation results"
                )
                raise SpanshNoResponse from ex
            if "error" in responses:
                logger.warning(f"Spansh encountered an error: {responses['error']}")
                return await ctx.reply(
                    "Spansh encountered an error processing and was unable to continue."
                )
            if (
                responses["status"] == "ok"
            ):  # Spansh has finised calculations for this job, add all inidvidual jump counts together
                jumps = 0
                for entry in responses["result"]["system_jumps"]:
                    jumps += entry["jumps"]
                job_results.append(jumps)
                break
            if spansh_loop_timeout <= 0:
                logger.exception("spansh took too long to calculate a route")
                raise SpanshResponseTimedOut
            spansh_loop_timeout -= 1
            await asyncio.sleep(1)
    await ctx.reply(
        f"{ctx.sender}: It will take about {job_results[0]} normal jumps or {job_results[1]} spansh jumps to get from {pointa_pretty} to {pointb_pretty} with a range of {jump_range} LY."
    )
    # Shorten the spansh results URL if the yourls module is enabled
    sysa = sysa.replace(" ", "%20")
    sysb = sysb.replace(" ", "%20")
    short = f"{config.spansh.page_uri}/{jobs[1]}?efficiency=60&from={sysa}&to={sysb}&range={jump_range}"
    if config.yourls.enabled:
        short = await shorten(short)
    return await ctx.reply(f"Here's a spansh URL: {short}")


async def spansh(
    ctx: Context,
    jump_range: float,
    sysa: str,
    sysb: str,
    pointa_pretty: str,
    pointb_pretty: str,
):
    """
    Starts calculating the normal and Neutron Jump Count using spansh.co.uk

    Args:
        ctx (Context): PYDLE Context
        jump_range (str): Ship's jump range
        sysa (str): Starting system
        sysb (str): Client's/Target system
        pointa_pretty (str): Starting system pre-formatted
        pointb_pretty (str): Client's/Target system pre-formatted

    Returns:
        ctx.reply()

    Raises:
        SpanshNoResponse: spansh did not respond in time.
        SpanshBadResponse: Spansh returned an unprocessable response
    """
    efficiency = [100, 60]
    job_id = []
    for percent in efficiency:
        params = {
            "efficiency": percent,
            "range": jump_range,
            "from": sysa,
            "to": sysb,
        }
        try:
            responses = await web_get(config.spansh.route_uri, params)
        except aiohttp.ClientError as ex:
            logger.exception(
                "spansh did not respond while trying to start the normal jump count calculation "
            )
            raise SpanshNoResponse from ex
        if "error" in responses:
            logger.warning(f"Spansh encountered an error: {responses['error']}")
            if responses["error"] == "Could not find starting system":
                return await ctx.reply("Spansh was unable to find the Starting System.")
            if responses["error"] == "Could not find finishing system":
                return await ctx.reply("Spansh was unable to find the Target System.")
            return await ctx.reply(
                "Spansh encountered an error processing and was unable to continue."
            )
        if "job" not in responses:
            raise SpanshBadResponse
        job_id.append(responses["job"])
    asyncio.create_task(
        spansh_get_routes(
            ctx, jump_range, sysa, sysb, pointa_pretty, pointb_pretty, job_id
        )
    )

    return await ctx.reply("Spansh calculations have been started...")
