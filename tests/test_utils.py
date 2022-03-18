"""
HalpyBOT v1.5.2

test_utils.py - miscellaneous utility functions module tests

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

NOTE: For these tests, it is advised to run pytest with the -W ignore::DeprecationWarning due to framework issues.
"""
import os.path
import pytest
from halpybot.packages.utils import get_time_seconds, language_codes, strip_non_ascii
from halpybot.packages.command import get_help_text


# Test Time
@pytest.mark.asyncio
async def test_seconds():
    time = await get_time_seconds("12:34:56")
    assert time == "45296"


# Test Bad Time
@pytest.mark.asyncio
async def test_seconds_bad():
    with pytest.raises(ValueError):
        await get_time_seconds("BACON")


# Test Lang Codes
# 1: If the file exists, we will assume it is correct.
def test_lang():
    assert os.path.exists("data/languages/iso639-1.json") is True


# 2: Check if the file returns a dict
def test_lang_content():
    langs = language_codes()
    assert isinstance(langs, dict)


# Test Strip ASCII
# 1: Strip non-ascii
def test_strip():
    string = strip_non_ascii("This has Non-Ascii ö to Strip")
    assert string == ("This has Non-Ascii  to Strip", True)


# 2: Nothing to Strip
def test_non_strip():
    string = strip_non_ascii("This has Non-Ascii to Strip")
    assert string == ("This has Non-Ascii to Strip", False)


# Test Help Commands
# 1: If the file exists, we will assume it is correct.
async def test_commands():
    assert os.path.exists("data/help/commands.json") is True


# 2: Check a help command response. If it returns a not none value, we will assume it is true.
async def test_commands_content():
    assert get_help_text("ping") is not None


# Test backup_facts Commands
# If the file exists, we will assume it is correct.
@pytest.mark.asyncio
async def test_backup_facts_file():
    assert os.path.exists("data/facts/backup_facts.json") is True


# TODO: Test Backup Fact with Fact test module


# Test EDSM files
# 1: If the file exists, we will assume it is correct.
@pytest.mark.asyncio
async def test_dssa_file():
    assert os.path.exists("data/edsm/dssa.json") is True


# 1: If the file exists, we will assume it is correct.
@pytest.mark.asyncio
async def test_landmark_file():
    assert os.path.exists("data/edsm/landmarks.json") is True


# Test announcer file
# 1: If the file exists, we will assume it is correct.
@pytest.mark.asyncio
async def test_announcer_file():
    assert os.path.exists("data/announcer/announcer.json") is True
