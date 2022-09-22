"""
test_delayed.py - Database interaction for Delayed Board module tests

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

NOTE: These tests interact with a database. It is REQUIRED to manually set an SQL server IP to run these queries on.
      If this IP is not given, the test will skip.
"""

import pytest
from halpybot.packages.delayedboard import DelayedCase
from halpybot.packages.configmanager import config

SAFE_IP = "an ip addr here"
CONFIG_IP = config["Database"]["Host"]
GOOD_IP = False
TEST_ID = ""
CURR_DELAYED = ""

if CONFIG_IP == SAFE_IP:
    GOOD_IP = True

pytestmark = pytest.mark.skipif(
    GOOD_IP is not True, reason="No safe IP Given! Unsafe to test."
)

pytestmark = pytest.mark.skipif(
    config["Offline Mode"]["enabled"] == "True",
    reason="Offline Mode Enabled on database-modifying tests! "
    "Please disable it to continue",
)


@pytest.mark.asyncio
async def test_open():
    """Test that a delayed case can be opened"""
    global TEST_ID, CURR_DELAYED
    CURR_DELAYED = await DelayedCase.check()
    opened = await DelayedCase.open(
        "1", "This is a test opened by HalpyBOTs Test Library", "HalpyBOT Test Library"
    )
    TEST_ID = opened[0]
    assert opened[1] == 0


@pytest.mark.asyncio
async def test_check():
    """Test that the number of delayed cases can be tested for"""
    checked_number = await DelayedCase.check()
    assert int(checked_number) > int(CURR_DELAYED)


@pytest.mark.asyncio
async def test_close():
    """Test that a delayed case be closed"""
    closed = await DelayedCase.status(int(TEST_ID), 3, "HalpyBOT Test Library")
    assert closed[1] == 0


@pytest.mark.asyncio
async def test_reopen():
    """Test that a delayed case can be reopened"""
    reopen = await DelayedCase.reopen(int(TEST_ID), "2", "HalpyBOT Test Library")
    assert reopen[1] == 0


@pytest.mark.asyncio
async def test_notes():
    """Test that case notes can be modified"""
    notes = await DelayedCase.notes(
        int(TEST_ID), "Modified Case Notes", "HalpyBOT Test Library"
    )
    assert notes[1] == 0


@pytest.mark.asyncio
async def test_close2():
    """Repeat the closure of the precvious test. Leave the system clean!"""
    closed = await DelayedCase.status(int(TEST_ID), 3, "HalpyBOT Test Library")
    assert closed[1] == 0
