"""
test_checks.py - Permission check module tests

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import pytest
from halpybot.packages.checks import (
    Pup,
    Drilled,
    Moderator,
    Admin,
    Cyberseal,
    Cybermgr,
    Owner,
)
from halpybot.packages.models import User


@pytest.mark.asyncio
async def test_permission_configs():
    """Test if levels match their expected returns"""
    levels = {
        (Pup, 1),
        (Drilled, 2),
        (Moderator, 3),
        (Admin, 4),
        (Cyberseal, 5),
        (Cybermgr, 6),
        (Owner, 7),
    }
    for level_name, level_num in levels:
        assert level_name.level == level_num


@pytest.mark.asyncio
async def test_permission_level_none():
    """Test if incorrectedly formatted VHOSTS return expected values"""
    vhost_tests = ["notaseal@abcdefg.hijklmnop", "this is garbage", "dQw4w9WgXcQ", None]
    for given_host in vhost_tests:
        vhost = User.process_vhost(given_host)
        assert vhost is None


@pytest.mark.asyncio
async def test_permission_level():
    """Test if VHOSTS return their expected values"""
    vhost_tests = {
        ("rixxan@rixxan.admin.hullseals.space", "rixxan.admin.hullseals.space"),
        ("seal@seal.cybersealmgr.hullseals.space", "cybersealmgr.hullseals.space"),
        ("seal@seal.cyberseal.hullseals.space", "cyberseal.hullseals.space"),
        ("seal@seal.moderator.hullseals.space", "moderator.hullseals.space"),
        ("seal@seal.seal.hullseals.space", "seal.hullseals.space"),
        ("seal@seal.pup.hullseals.space", "pup.hullseals.space"),
        ("seal@seal.admin.hullseals.space", "admin.hullseals.space"),
    }
    for given_host, expected_host in vhost_tests:
        vhost = User.process_vhost(given_host)
        assert vhost == expected_host


@pytest.mark.asyncio
async def test_permission_level_rix():
    """Test if special users VHOSTS are returned as expected"""
    vhost = User.process_vhost("rixxan.admin.hullseals.space")
    assert vhost == "rixxan.admin.hullseals.space"


@pytest.mark.asyncio
async def test_permission_level_comparisons():
    """Test that Permission Levels are sorted correctly"""
    assert (
        Pup.level
        < Drilled.level
        < Moderator.level
        < Admin.level
        < Cyberseal.level
        < Cybermgr.level
        < Owner.level
    )
