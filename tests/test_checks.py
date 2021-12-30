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
from src.packages.models import User


# Do the levels line up with expected permissions?
@pytest.mark.asyncio
async def test_config_write():
    levels = {(Pup, 1), (Drilled, 2), (Moderator, 3), (Admin, 4), (Cyberseal, 5), (Cybermgr, 6), (Owner, 7)}
    for level_name, level_num in levels:
        assert level_name.level == level_num


@pytest.mark.asyncio
async def test_permission_level_none():
    vhost_tests = ["notaseal@abcdefg.hijklmnop", "this is garbage", "dQw4w9WgXcQ", None]
    for given_host in vhost_tests:
        vhost = User.process_vhost(given_host)
        assert vhost is None


# Check returned VHOST of user
@pytest.mark.asyncio
async def test_permission_level():
    vhost_tests = {
        ("rixxan@rixxan.admin.hullseals.space", "rixxan.admin.hullseals.space"),
        ("seal@seal.cybersealmgr.hullseals.space", "cybersealmgr.hullseals.space"),
        ("seal@seal.cyberseal.hullseals.space", "cyberseal.hullseals.space"),
        ("seal@seal.moderator.hullseals.space", "moderator.hullseals.space"),
        ("seal@seal.seal.hullseals.space", "seal.hullseals.space"),
        ("seal@seal.pup.hullseals.space", "pup.hullseals.space"),
        ("seal@seal.admin.hullseals.space", "admin.hullseals.space")
    }
    for given_host, expected_host in vhost_tests:
        vhost = User.process_vhost(given_host)
        assert vhost == expected_host


@pytest.mark.asyncio
async def test_permission_level_rix():
    vhost = User.process_vhost("rixxan.admin.hullseals.space")
    assert vhost == "rixxan.admin.hullseals.space"
