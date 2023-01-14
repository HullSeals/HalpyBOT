"""
test_server.py - Permission check module tests

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import pytest
from halpybot.server.server import server_root


# FIXME: This test is not functioning correctly.
# @pytest.mark.asyncio
# async def test_root():
#     """Test the server responds properly to a GET / query"""
#     mac = await server_root("bacon")
#     assert mac.status == 200
