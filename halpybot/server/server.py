"""
server.py - Hull Seals API -> HalpyBOT server

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

"""
from typing import Type, Union
from datetime import datetime
from loguru import logger
import git
from aiohttp.web import Request, StreamResponse
from aiohttp import web
from aiohttp.web_exceptions import HTTPBadRequest, HTTPMethodNotAllowed, HTTPNotFound
from halpybot import __version__, DEFAULT_USER_AGENT
from ..packages.configmanager import config
from ..packages.ircclient import client as botclient


routes = web.RouteTableDef()


class HalpyServer(web.Application):
    async def __filter_request(
        self, request: Request
    ) -> Union[Type[HTTPBadRequest], None, HTTPMethodNotAllowed, HTTPNotFound]:
        """A method to filter out spam requests that would otherwise result
        in a large error message and log them neatly"""
        # Add Connection Logger
        connection_logger = logger.bind(task="API")
        # If they don't provide authentication, we log it and return 400
        request_method = request.method
        request_path = request.path

        if request_method == "POST":
            if (
                request.headers.get("hmac") is None
                or request.headers.get("keyCheck") is None
            ):
                connection_logger.info("Request submitted with incomplete auth headers")
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
            connection_logger.info("API request made for not used method")
            return HTTPMethodNotAllowed(
                request_method, list({route.method for route in routes})
            )
        connection_logger.info("API request made with unused path")
        return HTTPNotFound()

    async def _handle(self, request: Request) -> StreamResponse:
        # Add Connection Logger
        connection_logger = logger.bind(task="API")
        try:
            request_error = await self.__filter_request(request)
            if request_error is not None:
                connection_logger.info(
                    "Invalid request submitted by {host} not processed",
                    host=request.host,
                )
                raise request_error
            response = await super()._handle(request)
            return response
        except web.HTTPError as ex:
            return ex


@web.middleware
async def compression_middleware(request, handler):
    """Enable compression to improve our responses"""
    response = await handler(request)
    response.enable_compression()
    return response


@routes.get("/")
async def server_root(request):
    """
    Get the key information about the Bot

    Args:
        request (class): An object containing the content of the HTTP request.

    Returns:
        The formatted JSON response of the bot status

    """
    try:
        repo = git.Repo()
        sha = repo.head.object.hexsha
        sha = sha[0:7]
        sha = f" build {sha}"
    except git.InvalidGitRepositoryError:
        sha = ""
    server_status_nick = botclient.nickname  # FIXME unsynchronized cross-thread read
    if server_status_nick == "<unregistered>":
        server_status_nick = "Not Connected"
    response = {
        "app": DEFAULT_USER_AGENT,
        "version": f"{__version__}{sha}",
        "bot_nick": server_status_nick,
        "irc_connected": "True" if botclient.connected else "False",
        "offline_mode": config["Offline Mode"]["enabled"],
        "timestamp": datetime.utcnow().replace(microsecond=0).isoformat(),
    }
    return web.json_response(response)


APIConnector = HalpyServer(middlewares=[compression_middleware])
APIConnector.add_routes(routes)
