"""
test_database.py - Database connection initialization module tests

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import time
import pytest
from halpybot.packages.database import latency
from halpybot import config

pytestmark = pytest.mark.skipif(
    config.offline_mode.enabled,
    reason="Offline Mode Enabled on database-touching tests! "
    "Please disable it to continue",
)


# FIXME: Rework for Inbuilt Tests
# @pytest.mark.asyncio
# async def test_latency():
#     """Test the Database Latency.
#
#     If it's above 15, the connection is unusable."""
#     start = time.time()
#     connection = await latency()
#     final = round(connection - start, 2)
#     assert final < 15
