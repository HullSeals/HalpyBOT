"""
test_server.py - Server module tests

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import json
import aiohttp
from aiohttp import web
from aiohttp.test_utils import make_mocked_request
import pytest
from halpybot import DEFAULT_USER_AGENT, config
from halpybot.server.auth import get_hmac
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
    msg = json.dumps(body)
    msg = "".join(msg.split())
    mac = get_hmac(msg).hexdigest()
    check = get_hmac(
        config.api_connector.key_check_constant.get_secret_value()
    ).hexdigest()
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False),
        headers={"User-Agent": DEFAULT_USER_AGENT, "hmac": mac, "keyCheck": check},
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
