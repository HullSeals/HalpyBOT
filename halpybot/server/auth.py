"""
auth.py - Bare bones HAPIC authentication system

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import functools
import hmac
import hashlib
import json
from loguru import logger
from aiohttp import web
from halpybot import config


def get_hmac(msg: str) -> hmac.HMAC:
    """
    Calculate the HMAC value for message validation

    Args:
        msg (str): A jsondump of the message sent to the server.

    Returns:
        A new hmac object
    """
    return hmac.new(
        bytes(config.api_connector.key.get_secret_value(), "utf8"),
        msg=msg.encode("utf8"),
        digestmod=hashlib.sha256,
    )


def authenticate(function):
    """Validate a response coming in and check it against our config"""

    @functools.wraps(function)
    async def guarded(request):
        # Add Connection Logger
        with logger.contextualize(task="API"):
            data = await request.json()
            clientmac = request.headers.get("hmac")
            key_check = request.headers.get("keyCheck")

            msg = json.dumps(data)
            # Remove all whitespace for the purpose of ensuring identical inputs to HMAC
            msg = "".join(msg.split())
            mac = get_hmac(msg)
            check = hmac.new(
                bytes(config.api_connector.key.get_secret_value(), "utf8"),
                msg=config.api_connector.key_check_constant.get_secret_value().encode(
                    "utf8"
                ),
                digestmod=hashlib.sha256,
            )
            # Check to see if the key is correct using static message.
            # If wrong, return 401 unauthorised
            if not hmac.compare_digest(key_check, check.hexdigest()):
                logger.warning(
                    "Failed authentication. Incorrect key or key verification message"
                )
                raise web.HTTPUnauthorized()
            # If the key is correct but HMAC is different, the body has been altered in transit and should be rejected
            if not hmac.compare_digest(clientmac, mac.hexdigest()):
                logger.warning("Failed authentication. Bad request body")
                raise web.HTTPUnprocessableEntity()
            logger.info("Successfully authenticated API request")
        return await function(request)

    return guarded
