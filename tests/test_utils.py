"""
HalpyBOT v1.5

test_utils.py - miscellaneous utility functions module tests

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

NOTE: For these tests, it is advised to run pytest with the -W ignore::DeprecationWarning due to framework issues.
"""
import pytest
import os.path
from src.packages.utils import *


# Test Time
@pytest.mark.asyncio
async def test_seconds():
    time = await get_time_seconds("12:34:56")
    assert time == "45296"


# Test Lang Codes
# 1: If the file exists, we will assume it is correct.
@pytest.mark.asyncio
def test_lang():
    langs = os.path.exists("data/languages/iso639-1.json")
    assert langs is True


# 2: Check if the file returns a dict
@pytest.mark.asyncio
def test_lang_content():
    langs = language_codes()
    assert type(langs) == dict


# Test Strip ASCII
# 1: Strip non-ascii
@pytest.mark.asyncio
def test_strip():
    string = strip_non_ascii("This has Non-Ascii ö to Strip")
    assert string == ("This has Non-Ascii  to Strip", True)


# 2: Nothing to Strip
@pytest.mark.asyncio
def test_non_strip():
    string = strip_non_ascii("This has Non-Ascii to Strip")
    assert string == ("This has Non-Ascii to Strip", False)
