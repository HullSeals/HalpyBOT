"""
test_server.py - Permission check module tests

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
import aiohttp
from aiohttp import web
from aiohttp.test_utils import make_mocked_request
import pytest

from halpybot import DEFAULT_USER_AGENT, config
from halpybot.server.server import server_root, APIConnector
from tests.fixtures import TestBot


@pytest.mark.asyncio
async def test_root(bot_fx: TestBot):
    """Test the server responds properly to a GET / query"""
    request = make_mocked_request("GET", "/")
    request.app["botclient"] = bot_fx
    mac = await server_root(request)
    assert mac.status == 200


@pytest.mark.asyncio
async def test_announce(bot_fx: TestBot):
    """Test the server responds properly to a POST /announce query"""
    runner = web.AppRunner(APIConnector)
    runner.app["botclient"] = bot_fx
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", port=config.api_connector.port)
    await site.start()
    body = {
        "type": "SEALCASE",
        "parameters": {
            "Platform": "5",
            "CMDR": "InHoomansLeftEar2",
            "System": "Sol",
            "Hull": "25",
        },
    }
    hmac = "1b06dff4ed1755f17c108a5a501ff62352ae5f61cee3052dce74aae22326725e"
    keyCheck = "85035ef5eee3c98b4898d2047012a20e828324cf3abf037db2f6de922a5049d2"
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False),
        headers={"User-Agent": DEFAULT_USER_AGENT, "hmac": hmac, "keyCheck": keyCheck},
    ) as session:
        async with await session.post(
            f"http://127.0.0.1:{config.api_connector.port}/announce", json=body
        ) as response:
            assert response.status == 200
    await site.stop()
    assert bot_fx.sent_messages[0] == {
        "message": "xxxx PCLCASE -- NEWCASE xxxx\nCMDR: InHoomansLeftEar2 -- Platform: "
        "LIVE HORIZONS\nSystem: SOL -- Hull: 25\nxxxx Case ID: 1 xxxx\nSystem"
        " exists in EDSM, 0.0 LY South of Sol.",
        "target": "#bot-test",
    }
