"""
HalpyBOT v1.5

test_delayed.py - DDatabase interaction for Delayed Board module tests

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

NOTE: For these tests, it is advised to run pytest with the -W ignore::DeprecationWarning due to framework issues.
"""
import pytest
from src.packages.delayedboard import *
from src.packages.configmanager import config

devIP = "18.221.145.196"
configIP = config['Database']['Host']
goodIP = False
testID = ""
curr_delayed = ""

if configIP != devIP:
    assert False, "Tests attempted without confirming the Development IP addr. Please ensure you are running the Dev DB"
elif configIP == devIP:
    goodIP = True

if goodIP is True:
    @pytest.mark.asyncio
    async def test_open():
        global testID, curr_delayed
        curr_delayed = await DelayedCase.check()
        opened = await DelayedCase.open("1", "This is a test opened by HalpyBOTs Test Library", "HalpyBOT Test Library")
        testID = opened[0]
        assert opened[1] == 0


    @pytest.mark.asyncio
    async def test_check():
        checked_number = await DelayedCase.check()
        assert int(checked_number) > curr_delayed


    @pytest.mark.asyncio
    async def test_close():
        closed = await DelayedCase.status(testID, "3", "HalpyBOT Test Library")
        assert closed[1] == 0


    @pytest.mark.asyncio
    async def test_reopen():
        reopen = await DelayedCase.reopen(testID, "2", "HalpyBOT Test Library")
        assert reopen[1] == 0


    @pytest.mark.asyncio
    async def test_notes():
        notes = await DelayedCase.notes(testID, "Modified Case Notes", "HalpyBOT Test Library")
        assert notes[1] == 0


    @pytest.mark.asyncio
    async def test_close2():
        closed = await DelayedCase.status(testID, "3", "HalpyBOT Test Library")
        assert closed[1] == 0
