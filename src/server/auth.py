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

def Authenticate():
    def decorator(function):
        @functools.wraps(function)
        async def guarded(request):
            data = await request.json()
            clientmac = request.headers.get('hmac')
            msg = json.dumps(data, indent=4)
            mac = hmac.new(bytes(client_secret, 'utf8'), msg=msg.encode('utf8'), digestmod=hashlib.sha256)
            if not hmac.compare_digest(clientmac, mac.hexdigest()):
                raise web.HTTPUnauthorized()
            else:
                return await function(request)
        return guarded
    return decorator
