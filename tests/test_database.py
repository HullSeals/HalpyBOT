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


@pytest.mark.asyncio
async def test_latency(bot_fx):
    """Test the Database Latency.

    If it's above 15, the connection is unusable."""
    start = time.time()
    connection = await latency(bot_fx.engine)
    final = round(connection - start, 2)
    assert final < 15
