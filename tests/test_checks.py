"""
HalpyBOT v1.5

test_checks.py - Permission check module tests

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

NOTE: For these tests, it is advised to run pytest with the -W ignore::DeprecationWarning due to framework issues.
"""
import pytest
from src.packages.checks import *


# Do the levels line up with expected permissions?
@pytest.mark.asyncio
async def test_config_write():
    levels = {(Pup, 1), (Drilled, 2), (Moderator, 3), (Admin, 4), (Cyberseal, 5), (Cybermgr, 6), (Owner, 7)}
    for level_name, level_num in levels:
        assert level_name.level == level_num
