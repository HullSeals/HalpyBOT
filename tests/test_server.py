"""
test_server.py - Permission check module tests

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
from aiohttp.test_utils import make_mocked_request
import pytest
from halpybot.server.server import server_root
from tests.fixtures import TestBot


@pytest.mark.asyncio
async def test_root(bot_fx: TestBot):
    """Test the server responds properly to a GET / query"""
    request = make_mocked_request("GET", "/")
    request.app["botclient"] = bot_fx
    mac = await server_root(request)
    assert mac.status == 200
