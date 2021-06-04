"""
HalpyBOT v1.4

rank_change.py - Handler for Seal vhost changes requested by the API

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

"""

from typing import Dict
from aiohttp import web

from .server import APIConnector, HalpyClient
from .auth import Authenticate
from ..packages.database import DatabaseConnection, NoDatabaseConnection

routes = web.RouteTableDef()

@routes.post('/tail')
@Authenticate()
async def tail(request):
    if request.body_exists:
        request = await request.json()
    # Parse arguments
    rank = request["rank"]
    subject = request["subject"]
    result = None
    try:
        vhost = f"{subject}.{rank}.hullseals.space"
        await HalpyClient.client.rawmsg("hs", "SETALL", subject, vhost)
        raise web.HTTPOk
    except NoDatabaseConnection:
        raise

APIConnector.add_routes(routes)
