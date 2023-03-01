"""
conftest.py - Fixture Developement Workshop

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
import os
import pytest

if os.getcwd().endswith("tests"):
    os.chdir("..")

# noinspection PyUnresolvedReferences
from halpybot import commands, config
from .fixtures.mock_halpy import TestBot


@pytest.fixture()
async def bot_fx() -> TestBot:
    """Create a fixture that represents the bot"""
    test_bot = TestBot(nickname="HalpyTest[BOT]")
    return test_bot


@pytest.fixture()
async def db_engine(bot_fx: bot_fx):
    """Create a db_engine fixture"""
    config.offline_mode.enabled = False
    return bot_fx.engine
