"""
HalpyBOT v1.4

server.py - Hull Seals API -> HalpyBOT server

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

"""

from aiohttp import web
import pydle
from typing import Optional

from src import __version__

class BotClient:

    def __init__(self, client: Optional[pydle.Client] = None):
        """Ridiculously hacky way for us to get the IRC client

        Circular imports can bite my tail.

        Args:
            client (pydle.Client or None): Pydle client

        """
        self._client = client

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, client: Optional[pydle.Client] = None):
        self._client = client


HalpyClient = BotClient()
routes = web.RouteTableDef()

@routes.get('/')
async def server_root(request):
    response = {"app": "Hull Seals HalpyBOT",
                "version": __version__,
                "bot_nick": HalpyClient.client.nickname}
    return web.json_response(response)

APIConnector = web.Application()
APIConnector.add_routes(routes)
