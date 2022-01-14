"""
HalpyBOT v1.5

server.py - Hull Seals API -> HalpyBOT server

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

"""
from typing import Union
import aiohttp.web
from aiohttp import web
from aiohttp.web import Request, StreamResponse
import asyncio
import logging
from datetime import datetime
from ..packages.configmanager import config

from aiohttp.web_exceptions import HTTPBadRequest, HTTPClientError, HTTPMethodNotAllowed, HTTPNotFound

from src import __version__
from ..packages.ircclient import client as botclient
from ..packages.database import DatabaseConnection, NoDatabaseConnection

logger = logging.getLogger(__name__)

routes = web.RouteTableDef()


class HalpyServer(web.Application):

    @staticmethod
    async def _log_request(request: Request, success: bool):
        # Log to the online dashboard
        try:
            with DatabaseConnection() as db:
                cursor = db.cursor()
                cursor.callproc('spCreateAPIConnRequest', [request.remote,  # Source
                                                           (request.headers['User-Agent'] if
                                                            'User-Agent' in request.headers else "None"),  # Agent
                                                           request.path,  # Route
                                                           request.method,  # HTTP Method
                                                           (str(await request.json()) if request.has_body else
                                                            "None"),  # Body
                                                           (1 if success else 0),  # HMAC match
                                                           str(request.version)  # Misc
                                                           ])
        except NoDatabaseConnection:
            # TODO: stash call and run later when reconnected
            pass

    async def __filter_request(self, request: Request) -> Union[None, HTTPClientError]:
        """A method to filter out spam requests that would otherwise result
        in a large error message and log them neatly"""
        # If they don't provide authentication, we log it and return 400
        request_method = request.method
        request_path = request.path

        if request_method == "POST":
            if request.headers.get("hmac") is None or request.headers.get("keyCheck") is None:
                logger.info("Request submitted with incomplete auth headers")
                return HTTPBadRequest

        no_method = True
        registered_routes = self.router.routes()
        for route in registered_routes:
            if route.method == request_method:
                no_method = False
                # The amount of time I spent looking through the documentation for where they keep the list of routes
                # The route.resource.canonical SHOULD (tm) be the path for the route
                if route.resource.canonical == request_path:
                    return None
        if no_method:
            logger.info("API request made for not used method")
            return HTTPMethodNotAllowed(request_method, list({route.method for route in routes}))
        logger.info("API request made with unused path")
        return HTTPNotFound()

    async def _handle(self, request: Request) -> StreamResponse:
        successful = True
        try:
            request_error = await self.__filter_request(request)
            if request_error is not None:
                logger.info(f"Invalid request submitted by {request.host} not processed")
                raise request_error
            else:
                response = await super()._handle(request)
                successful = True
                return response
        except aiohttp.web.HTTPError as ex:
            successful = False
            return ex
        finally:
            asyncio.ensure_future(self._log_request(request, successful))



@routes.get('/')
async def server_root(request):
    response = {"app": "Hull Seals HalpyBOT",
                "version": __version__,
                "bot_nick": botclient.nickname,
                "irc_connected": "True" if botclient.connected else "False",
                "offline_mode": config['Offline Mode']['enabled'],
                "timestamp": datetime.utcnow().replace(microsecond=0).isoformat()
                }
    return web.json_response(response)

APIConnector = HalpyServer()
APIConnector.add_routes(routes)
