"""
HalpyBOT v1.6

test_database.py - Database connection initialization module tests

Copyright (c) 2022 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

NOTE: For these tests, it is advised to run pytest with the -W ignore::DeprecationWarning due to framework issues.
"""

import time
import pytest
from halpybot.packages.database import latency
from halpybot.packages.configmanager import config

pytestmark = pytest.mark.skipif(
    config["Offline Mode"]["enabled"] == "True",
    reason="Offline Mode Enabled on database-touching tests! "
    "Please disable it to continue",
)


@pytest.mark.asyncio
async def test_latency():
    """Test the Database Latency.

    If it's above 15, the connection is unusable."""
    start = time.time()
    connection = await latency()
    final = round(connection - start, 2)
    assert final < 15
