"""
HalpyBOT v1.5

test_seals.py - Fetching information about a registered user module tests

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

NOTE: For these tests, it is advised to run pytest with the -W ignore::DeprecationWarning due to framework issues.
"""
import pytest
from src.packages.seals import *


# Test Time
# 1: Test a good user with a valid WHOIS
@pytest.mark.asyncio
async def test_good_whois():
    user = await whois("HalpyBOT")
    user = user[:len(user) // 2]
    assert user == "CMDR HalpyBOT has a Seal ID of 235, registered on 2019-12-20, is a DW2 Veteran and Founder Seal"


@pytest.mark.asyncio
async def test_bad_whois():
    user = await whois("ThisCMDRDoesntExist")
    assert user == "No registered user found by that name!"
