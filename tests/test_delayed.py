"""
HalpyBOT v1.5.2

test_delayed.py - DDatabase interaction for Delayed Board module tests

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

NOTE: For these tests, it is advised to run pytest with the -W ignore::DeprecationWarning due to framework issues.

NOTE: These tests interact with a database. It is REQUIRED to manually set an SQL server IP to run these queries on.
      If this IP is not given, the test will skip.
"""
import pytest
from halpybot.packages.delayedboard import *
from halpybot.packages.configmanager import config

safeIP = ""
configIP = config["Database"]["Host"]
goodIP = False
testID = ""
curr_delayed = ""

if configIP == safeIP:
    goodIP = True

pytestmark = pytest.mark.skipif(
    goodIP is not True, reason="No safe IP Given! Unsafe to test."
)


@pytest.mark.asyncio
async def test_open():
    global testID, curr_delayed
    curr_delayed = await DelayedCase.check()
    opened = await DelayedCase.open(
        "1", "This is a test opened by HalpyBOTs Test Library", "HalpyBOT Test Library"
    )
    testID = opened[0]
    assert opened[1] == 0


@pytest.mark.asyncio
async def test_check():
    checked_number = await DelayedCase.check()
    assert int(checked_number) > int(curr_delayed)


@pytest.mark.asyncio
async def test_close():
    closed = await DelayedCase.status(int(testID), 3, "HalpyBOT Test Library")
    assert closed[1] == 0


@pytest.mark.asyncio
async def test_reopen():
    reopen = await DelayedCase.reopen(int(testID), "2", "HalpyBOT Test Library")
    assert reopen[1] == 0


@pytest.mark.asyncio
async def test_notes():
    notes = await DelayedCase.notes(
        int(testID), "Modified Case Notes", "HalpyBOT Test Library"
    )
    assert notes[1] == 0


@pytest.mark.asyncio
async def test_close2():
    closed = await DelayedCase.status(int(testID), 3, "HalpyBOT Test Library")
    assert closed[1] == 0
