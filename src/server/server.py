"""
HalpyBOT v1.4

server.py - Hull Seals API -> HalpyBOT server

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

"""

from aiohttp import web
from typing import List

from src import __version__

from ..packages.announcer import Announcer, AnnouncementError

routes = web.RouteTableDef()

@routes.get('/version')
async def server_get_version(request):
    return web.Response(text=__version__)

@routes.post('/announce')
async def test_announce(request):
    if request.body_exists:
        request = await request.json()
    response = {"status": None}
    # Parse arguments
    announcement = request["type"]
    args: List[str] = request["parameters"]
    try:
        await MainAnnouncer.announce(announcement=announcement, args=args)
        response["status"] = 200
    except AnnouncementError:
        response["status"] = 500
    return response

MainAnnouncer = Announcer()
APIConnector = web.Application()
APIConnector.add_routes(routes)
