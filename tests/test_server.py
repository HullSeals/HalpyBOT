"""
HalpyBOT v1.6

test_server.py - Permission check module tests

Copyright (c) 2022 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

NOTE: For these tests, it is advised to run pytest with the -W ignore::DeprecationWarning due to framework issues.
"""
import pytest
from halpybot.server.server import server_root


@pytest.mark.asyncio
async def test_root():
    mac = await server_root("bacon")
    assert mac.status == 200
