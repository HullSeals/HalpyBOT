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

from ..packages.configmanager import config


def get_hmac(msg):
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


const_key_check = hmac.new(
    bytes(config.api_connector.key.get_secret_value(), "utf8"),
    msg=config.api_connector.key_check_constant.get_secret_value().encode("utf8"),
    digestmod=hashlib.sha256,
)


def authenticate():
    """Validate a response coming in and check it against our config"""

    def decorator(function):
        @functools.wraps(function)
        async def guarded(request):
            # Add Connection Logger
            connection_logger = logger.bind(task="API")

            data = await request.json()
            clientmac = request.headers.get("hmac")
            key_check = request.headers.get("keyCheck")

            msg = json.dumps(data)
            msg = "".join(
                msg.split()
            )  # Remove all whitespace for the purpose of ensuring identical inputs to HMAC

            mac = get_hmac(msg)
            check = const_key_check
            # Check to see if the key is correct using static message.
            # If wrong, return 401 unauthorised
            if not hmac.compare_digest(key_check, check.hexdigest()):
                connection_logger.warning(
                    "Failed authentication. Incorrect key or key verification message"
                )
                raise web.HTTPUnauthorized()
            # If the key is correct but HMAC is different, the body has been altered in transit and should be rejected
            if not hmac.compare_digest(clientmac, mac.hexdigest()):
                connection_logger.warning("Failed authentication. Bad request body")
                raise web.HTTPUnprocessableEntity()
            connection_logger.info("Successfully authenticated API request")
            return await function(request)

        return guarded

    return decorator
