"""
rank_change.py - Handler for Seal vhost changes requested by the API

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

"""

from aiohttp import web
from loguru import logger
from sqlalchemy import text
from .server import APIConnector
from .auth import authenticate
from ..packages.database import engine, NoDatabaseConnection

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
    botclient = request.app["botclient"]
    if request.body_exists:
        request = await request.json()
    # Parse arguments
    rank = request["rank"]
    subject = request["subject"]
    try:
        vhost = f"{subject}.{rank}.hullseals.space"
        with engine.connect() as database_connection:
            result = database_connection.execute(
                text(
                    "SELECT nick FROM ircDB.anope_db_NickAlias WHERE nc = :subject_name;"
                ),
                subject_name=subject,
            )
            for i in result:
                logger.info(i)
                await botclient.rawmsg("hs", "SETALL", i[0], vhost)
            raise web.HTTPOk
    except NoDatabaseConnection:
        logger.exception("No database connection, unable to TAIL.")
        raise web.HTTPServiceUnavailable from NoDatabaseConnection


APIConnector.add_routes(routes)
