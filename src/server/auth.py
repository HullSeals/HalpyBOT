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

from ..packages.configmanager import config

client_secret = config['API Connector']['key']
checkConstant = config['API Connector']['key_check_constant']

def Authenticate():
    def decorator(function):
        @functools.wraps(function)
        async def guarded(request):
            data = await request.json()
            clientmac = request.headers.get('hmac')
            msg = json.dumps(data, indent=4)

            # Need CRLF (\r\n) instead of just LF
            # Not sure who's to blame for switching them. Leading candidate is maybe Ubuntu but Python is also a suspect
            CRLF_msg = msg.replace("\n", "\r\n")
            LF_msg = msg

            LF_mac = hmac.new(bytes(client_secret, 'utf8'), msg=LF_msg.encode('utf8'), digestmod=hashlib.sha256)
            CRLF_mac = hmac.new(bytes(client_secret, 'utf8'), msg=CRLF_msg.encode('utf8'), digestmod=hashlib.sha256)

            keyCheck = request.headers.get('keyCheck')
            check = hmac.new(bytes(client_secret, 'utf8'), msg = checkConstant.encode('utf8'), digestmod=hashlib.sha256)

            if not hmac.compare_digest(keyCheck, check.hexdigest()):
                raise web.HTTPUnauthorized()
            # Allows request body to use either CRLF or LF for new line. Should prevent this problem in the future
            elif not (hmac.compare_digest(clientmac, LF_mac.hexdigest()) or hmac.compare_digest(clientmac, CRLF_mac.hexdigest())):
                raise web.HTTPBadRequest()
            else:
                return await function(request)
        return guarded
    return decorator
