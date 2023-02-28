"""
test_seals.py - Fetching information about a registered user module tests

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

Testing will always DISABLE offline mode. You must have access to a Seal-type DB for testing.
"""

import pytest

from halpybot.packages.models import Seal
from halpybot.packages.seals import whois
from halpybot import config

config.offline_mode.enabled = False


@pytest.mark.asyncio
async def test_good_whois(bot_fx):
    """Test the WHOIS reply for a valid user"""
    user = await whois(bot_fx.engine, "rik079")
    assert isinstance(user, Seal)


@pytest.mark.asyncio
async def test_bad_whois(bot_fx):
    """Test the WHOIS reply for a valid user"""
    with pytest.raises(ValueError):
        await whois(bot_fx.engine, "blargnet")


@pytest.mark.asyncio
async def test_offline_whois(bot_fx):
    """Test that the WHOIS system responds properly in ONLINE mode"""
    prev_value = config.offline_mode.enabled
    config.offline_mode.enabled = True
    with pytest.raises(ValueError):
        await whois(bot_fx.engine, "ThisCMDRDoesntExist")
    config.offline_mode.enabled = prev_value
