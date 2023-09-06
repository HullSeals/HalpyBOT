"""
spansh.py - Your GPS for the Neutron Highway!

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
import string
from typing import List
from urllib.parse import quote
import asyncio
import aiohttp
from loguru import logger
from halpybot import config
from . import shorten, web_get
from ..exceptions import SpanshNoResponse, SpanshBadResponse, SpanshResponseTimedOut
from ..models import Context, Points


def sanitize_system_name(name: str) -> str:
    """
    Makes an effort to sanitize system input to help prevent SSRF or other web vulnerabilities
    """
    # Whitelist allowed characters (alphanumeric, hyphen, space)
    allowed_chars = f"- {string.ascii_letters}{string.digits}+.'*()/#’,"
    # Remove any disallowed characters from the system name
    sanitized_name = "".join(c for c in name if c in allowed_chars)
    return sanitized_name.strip()


@logger.catch(message="Unexpected error encountered in the Spansh Get_Route Function.")
async def spansh_get_routes(
    ctx: Context,
    points: Points,
    jobs: List[str],
) -> None:
    """
    Receives calculated Normal and Neutron Jump Counts from spansh.co.uk

    Args:
        ctx (Context): PYDLE Context
        points (Points): A pair of EDSM valid point locations and names, with a jump range
        jobs (list): A list of two Spansh processing jobs

    Returns:
        None

    Raises:
        aiohttp.ClientError: Error occurred during HTTP Request
        SpanshNoResponse: spansh did not respond in time.
        SpanshBadResponse: Spansh returned an unprocessable response
        SpanshResponseTimedOut: Spansh took too long to calculate a route
    """
    spansh_loop_timeout = config.spansh.calculations_timeout
    job_results = []
    for job in jobs:
        process_job = True
        while process_job:
            try:  # Receive current job status
                responses = await asyncio.wait_for(
                    web_get(f"{config.spansh.results_endpoint}/{job}"),
                    timeout=spansh_loop_timeout,
                )
            except aiohttp.ClientError as ex:
                logger.exception(
                    "Spansh did not respond while trying to receive the calculation results"
                )
                raise SpanshNoResponse from ex
            except asyncio.TimeoutError as ex:
                logger.exception("Spansh took too long to respond")
                raise SpanshResponseTimedOut from ex
            try:
                if responses["status"] == "ok":
                    # Spansh has finished calculations for this job, add all individual jump counts together
                    jumps = sum(
                        entry["jumps"] for entry in responses["result"]["system_jumps"]
                    )
                    job_results.append(jumps)
                    # Processing of this job has finished, exit the loop
                    process_job = False
            except KeyError as keyerr:
                logger.warning("Spansh returned an unprocessable response")
                logger.warning(responses)
                raise SpanshBadResponse from keyerr
    # Mention user since it may have been multiple seconds since they sent the calculation request
    response = (
        f"{ctx.sender}: It will take about {job_results[0]} normal jumps or {job_results[1]} spansh jumps to get from "
        f"{points.point_a.pretty} to {points.point_b.pretty} with a range of {points.jump_range} LY."
    )

    # Encode spaces to be URL compatible
    url_a = quote(sanitize_system_name(points.point_a.name))
    url_b = quote(sanitize_system_name(points.point_b.name))
    # Format spansh results URL with parameters
    short = f"{config.spansh.page_endpoint}/{jobs[1]}?efficiency=60&from={url_a}&to={url_b}&range={points.jump_range}"
    if config.yourls.enabled:
        short = await shorten(short)  # Shorten the URL if the yourls module is enabled
    return await ctx.reply(f"{response}\nHere's a spansh URL: {short}")


async def spansh(ctx: Context, points: Points) -> None:
    """
    Starts calculating the normal and Neutron Jump Count using spansh.co.uk

    Args:
        ctx (Context): PYDLE Context
        points (Points): A pair of EDSM valid point locations and names, with a jump range

    Returns:
        None

    Raises:
        SpanshNoResponse: spansh did not respond in time.
        SpanshBadResponse: Spansh returned an unprocessable response
    """
    efficiency = [100, 60]
    job_id = []
    for percent in efficiency:
        # Create request parameters for both Normal and Neutron Jump Calculations
        params = {
            "efficiency": percent,
            "range": points.jump_range,
            "from": sanitize_system_name(points.point_a.name),
            "to": sanitize_system_name(points.point_b.name),
        }
        try:  # Try to start Jump Calculations
            responses = await web_get(config.spansh.route_endpoint, params)
        except aiohttp.ClientError as ex:
            logger.exception(
                f"spansh did not respond while trying to start the {percent}% efficiency jump count calculation"
            )
            raise SpanshNoResponse from ex
        if "error" in responses:  # Process errors received from spansh
            logger.warning(f"Spansh encountered an error: {responses['error']}")
            if responses["error"] == "Could not find starting system":
                return await ctx.reply("Spansh was unable to find the Starting System.")
            if responses["error"] == "Could not find finishing system":
                return await ctx.reply("Spansh was unable to find the Target System.")
            # Other possible errors are issues with Range or efficiency,
            # those should not be possible as Range has been preprocessed and efficiencies are constants
            return await ctx.reply(
                "Spansh encountered an error processing and was unable to continue."
            )
        if "job" not in responses:
            # Spansh returned neither a job nor an error, something is wrong
            raise SpanshBadResponse
        job_id.append(responses["job"])
    # Calculations have been started, start checking and processing results
    asyncio.create_task(spansh_get_routes(ctx, points, job_id))
    return await ctx.reply("Spansh calculations have been started...")
