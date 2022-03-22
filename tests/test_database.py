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


# Test Database Latency
# If the latency is any greater than 15, the connection is unusable.
@pytest.mark.asyncio
async def test_latency():
    start = time.time()
    connection = await latency()
    final = round(connection - start, 2)
    assert final < 15
