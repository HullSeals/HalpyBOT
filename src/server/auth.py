import functools
import hmac
from aiohttp import web
import hashlib

from ..packages.configmanager import config

client_secret = config['API Connector']['key']

def Authenticate():
    def decorator(function):
        @functools.wraps(function)
        async def guarded(request):
            data = await request.json()
            clientmac = request.headers.get('hmac')
            mac = hmac.new(bytes(client_secret, 'utf8'), msg='123'.encode('utf8'), digestmod=hashlib.sha256)

            if not hmac.compare_digest(clientmac, mac.hexdigest()):
                raise web.HTTPUnauthorized()
            else:
                return await function(request)
        return guarded
    return decorator
