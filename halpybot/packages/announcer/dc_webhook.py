"""
dc_webhook.py - Discord webhook support

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

"""

from typing import Dict, Union, Optional
import aiohttp
from loguru import logger

from halpybot import DEFAULT_USER_AGENT


class DiscordWebhookError(Exception):
    """
    Base class for Discord webhook errors
    """


class WebhookSendError(DiscordWebhookError):
    """
    An exception occurred while sending a Discord Webhook
    """


async def send_webhook(
    hook_id: Optional[int],
    hook_token: str,
    body: Dict[str, Union[str, Dict[str, Union[str, bool, int]]]],
):
    """Send a webhook payload to Discord

    Args:
        hook_id (int): ID for the webhook as registered with Discord
        hook_token (str): Webhook token
        body (Dict): JSON body for the request, see Discord API documentation

    Returns:
        Nothing

    Raises:
        WebhookSendError: Unable to post webhook

    """
    try:
        async with aiohttp.ClientSession(
            headers={"User-Agent": DEFAULT_USER_AGENT}
        ) as session:
            await session.post(
                f"https://discord.com/api/webhooks/{hook_id}/{hook_token}", json=body
            )
    except aiohttp.ClientError as ex:
        logger.exception("Unable to send webhook")
        raise WebhookSendError from ex
