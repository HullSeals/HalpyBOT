"""
HalpyBOT v1.6

test_utils.py - miscellaneous utility functions module tests

Copyright (c) 2022 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

NOTE: For these tests, it is advised to run pytest with the -W ignore::DeprecationWarning due to framework issues.
"""
import os.path
import pytest
from halpybot.packages.utils import get_time_seconds, language_codes, strip_non_ascii
from halpybot.packages.command import get_help_text


@pytest.mark.asyncio
async def test_seconds():
    """Test the time system responds properly"""
    time = await get_time_seconds("12:34:56")
    assert time == "45296"


@pytest.mark.asyncio
async def test_seconds_bad():
    """Test the time system responds properly if an error occurs"""
    with pytest.raises(ValueError):
        await get_time_seconds("BACON")


def test_lang():
    """Test the lang files exist"""
    assert os.path.exists("data/languages/iso639-1.json") is True


def test_lang_content():
    """Test the lang file is formatted properly"""
    langs = language_codes()
    assert isinstance(langs, dict)


def test_strip():
    """Test ascii code can be stripped from a string"""
    string = strip_non_ascii("This has Non-Ascii ö to Strip")
    assert string == ("This has Non-Ascii  to Strip", True)


def test_non_strip():
    """Test ascii-compliant strings will be left alone"""
    string = strip_non_ascii("This has Non-Ascii to Strip")
    assert string == ("This has Non-Ascii to Strip", False)


async def test_commands():
    """Test the help file exists"""
    assert os.path.exists("data/help/commands.json") is True


async def test_commands_content():
    """Test the help file is formatted properly"""
    assert get_help_text("ping") is not None


@pytest.mark.asyncio
async def test_backup_facts_file():
    """Test the backup fact file exists"""
    assert os.path.exists("data/facts/backup_facts.json") is True


# TODO: Test Backup Fact with Fact test module


@pytest.mark.asyncio
async def test_dssa_file():
    """Test the DSSA file exists"""
    assert os.path.exists("data/edsm/dssa.json") is True


@pytest.mark.asyncio
async def test_landmark_file():
    """Test the landmark file exists"""
    assert os.path.exists("data/edsm/landmarks.json") is True


@pytest.mark.asyncio
async def test_announcer_file():
    """Test the announcer file exists"""
    assert os.path.exists("data/announcer/announcer.json") is True
