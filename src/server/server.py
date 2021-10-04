"""
HalpyBOT v1.5

server.py - Hull Seals API -> HalpyBOT server

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

"""

from aiohttp import web

from src import __version__
from ..packages.ircclient import client as botclient

routes = web.RouteTableDef()


@routes.get('/')
async def server_root(request):
    response = {"app": "Hull Seals HalpyBOT",
                "version": __version__,
                "bot_nick": botclient.nickname,
                "irc_connected": "True" if botclient.connected else "False"}
    return web.json_response(response)

APIConnector = web.Application()
APIConnector.add_routes(routes)
