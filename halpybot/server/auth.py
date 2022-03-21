"""
HalpyBOT v1.5.2

auth.py - Bare bones HAPIC authentication system

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import functools
import hmac
import hashlib
import json
import logging
from aiohttp import web

from ..packages.configmanager import config
from ..packages.database import Grafana

logger = logging.getLogger(__name__)
logger.addHandler(Grafana)

client_secret = config["API Connector"]["key"]
check_constant = config["API Connector"]["key_check_constant"]


def get_hmac(msg):
    return hmac.new(
        bytes(client_secret, "utf8"), msg=msg.encode("utf8"), digestmod=hashlib.sha256
    )


const_key_check = hmac.new(
    bytes(client_secret, "utf8"),
    msg=check_constant.encode("utf8"),
    digestmod=hashlib.sha256,
)


def authenticate():
    def decorator(function):
        @functools.wraps(function)
        async def guarded(request):
            data = await request.json()
            clientmac = request.headers.get("hmac")
            key_check = request.headers.get("keyCheck")

            msg = json.dumps(data)
            msg = "".join(
                msg.split()
            )  # Remove all whitespace for the purpose of ensuring identical inputs to HMAC

            mac = get_hmac(msg)
            check = const_key_check
            # Check to see if the key is correct using static message. If wrong, return 401 unauthorised
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

    return decorator
