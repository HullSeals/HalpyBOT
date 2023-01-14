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
from halpybot import commands
from .fixtures.mock_halpy import TestBot


# FIXME
# @pytest.fixture()
# async def bot_fx():
#     """Create a fixture that represents the bot"""
#
#     # noinspection PyProtectedMember
#     await Facts._from_local()  # Allows us to test the Fact module from the pre-packaged JSON file
#     test_bot = TestBot(nickname="HalpyTest[BOT]")
#     return test_bot
