"""
HalpyBOT v1.5

auth.py - Bare bones HAPIC authentication system

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import functools
import hmac
from aiohttp import web
import hashlib
import json
import logging

from ..packages.configmanager import config

logger=logging.getLogger(__name__)

client_secret = config['API Connector']['key']
checkConstant = config['API Connector']['key_check_constant']

def Authenticate():
    def decorator(function):
        @functools.wraps(function)
        async def guarded(request):
            data = await request.json()
            clientmac = request.headers.get('hmac')
            key_check = request.headers.get('keyCheck')
            
            msg = json.dumps(data)
            msg = ''.join(msg.split()) # Remove all whitespace for the purpose of ensuring identical inputs to HMAC

            mac = hmac.new(bytes(client_secret, 'utf8'), msg=msg.encode('utf8'), digestmod=hashlib.sha256)
            check = hmac.new(bytes(client_secret, 'utf8'), msg = checkConstant.encode('utf8'), digestmod=hashlib.sha256)
            # Check to see if the key is correct using static message. If wrong, return 401 unauthorised
            if not hmac.compare_digest(key_check, check.hexdigest()):
                logger.warning("Failed authentication. Incorrect key or key verification message")
                raise web.HTTPUnauthorized()
            # If the key is correct but HMAC is different, the body has been altered in transit and should be rejected
            elif not hmac.compare_digest(clientmac, mac.hexdigest()):
                logger.warning("Failed authentication. Bad request body")
                raise web.HTTPUnprocessableEntity()
            else:
                logger.info("Successfully authenticated API request")
                return await function(request)
        return guarded
    return decorator
