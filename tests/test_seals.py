"""
HalpyBOT v1.6

test_seals.py - Fetching information about a registered user module tests

Copyright (c) 2022 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

NOTE: For these tests, it is advised to run pytest with the -W ignore::DeprecationWarning due to framework issues.
"""
import pytest
from halpybot.packages.seals import whois
from halpybot.packages.configmanager import config, config_write


@pytest.mark.asyncio
async def test_good_whois():
    """Test the WHOIS reply for the fun name"""
    user = await whois("HalpyBOT")
    user = user[: len(user) // 2]
    assert (
        user
        == "CMDR HalpyBOT has a Seal ID of 235, registered on 2019-12-20, is a DW2 Veteran and Founder Seal"
    )


@pytest.mark.asyncio
async def test_bad_whois():
    """Test that the WHOIS system responds properly in ONLINE mode"""
    prev_value = config["Offline Mode"]["enabled"]
    config_write("Offline Mode", "enabled", "False")
    user = await whois("ThisCMDRDoesntExist")
    assert user == "No registered user found by that name!"
    config_write("Offline Mode", "enabled", prev_value)


@pytest.mark.asyncio
async def test_no_db():
    """Test that the WHOIS responds properly in offline mode"""
    prev_value = config["Offline Mode"]["enabled"]
    config_write("Offline Mode", "enabled", "True")
    no_database = await whois("ThisCMDRDoesntExist")
    assert no_database == "Error searching user."
    config_write("Offline Mode", "enabled", prev_value)
