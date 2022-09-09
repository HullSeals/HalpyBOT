"""
rank_change.py - Handler for Seal vhost changes requested by the API

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

"""

from aiohttp import web
from loguru import logger
from .server import APIConnector
from .auth import authenticate
from ..packages.database import DatabaseConnection, NoDatabaseConnection  # FIXME: SQLALCHEMY
from ..packages.ircclient import client as botclient

routes = web.RouteTableDef()


@routes.post("/tail")
@authenticate()
async def tail(request):
    """
    Promote or Demote a Seal on the status of their training

    Args:
        request (class): An object containing the content of the HTTP request.

    Returns:
        Nothing

    Raises:
        HTTPOK or HTTPServiceUnavailable
    """
    if request.body_exists:
        request = await request.json()
    # Parse arguments
    rank = request["rank"]
    subject = request["subject"]
    try:
        vhost = f"{subject}.{rank}.hullseals.space"
        with DatabaseConnection() as database_connection:
            cursor = database_connection.cursor()
            cursor.execute(
                "SELECT nick FROM ircDB.anope_db_NickAlias WHERE nc = %s;", (subject,)
            )
            result = cursor.fetchall()
            for i in result:
                await botclient.rawmsg("hs", "SETALL", i[0], vhost)
            raise web.HTTPOk
    except NoDatabaseConnection:
        logger.exception("No database connection, unable to TAIL.")
        raise web.HTTPServiceUnavailable from NoDatabaseConnection


APIConnector.add_routes(routes)
