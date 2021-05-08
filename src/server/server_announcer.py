"""
HalpyBOT v1.4

server_announcer.py - Handler for announcements requested by the API

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

"""

from typing import Dict
from aiohttp import web

from ..packages.announcer import Announcer, AnnouncementError
from .server import APIConnector

routes = web.RouteTableDef()

@routes.post('/announce')
async def announce(request):
    if request.body_exists:
        request = await request.json()
    # Parse arguments
    announcement = request["type"]
    args: Dict = request["parameters"]
    try:
        await MainAnnouncer.announce(announcement=announcement, args=args)
        raise web.HTTPOk
    except AnnouncementError:
        raise web.HTTPInternalServerError

MainAnnouncer = Announcer()

APIConnector.add_routes(routes)
