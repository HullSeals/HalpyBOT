"""
HalpyBOT v1.6

server_announcer.py - Handler for announcements requested by the API

Copyright (c) 2022 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

"""

from typing import Dict
from aiohttp import web
from ..packages.announcer import Announcer, AnnouncementError
from .server import APIConnector
from .auth import authenticate

routes = web.RouteTableDef()


@routes.post("/announce")
@authenticate()
async def announce(request):
    """
    Collect and format a new announcer system message from a POST request.

    Args:
        request (class): An object containing the content of the HTTP request.

    Returns:
        Nothing

    Raises:
        HTTPOk or HTTPInternalServerError
    """
    if request.body_exists:
        request = await request.json()
    # Parse arguments
    announcement = request["type"]
    args: Dict = request["parameters"]
    try:
        await MainAnnouncer.announce(announcement=announcement, args=args)
        raise web.HTTPOk
    except AnnouncementError:
        raise web.HTTPInternalServerError from AnnouncementError


MainAnnouncer = Announcer()

APIConnector.add_routes(routes)
