"""
HalpyBOT v1.5

test_edsm.py - Elite: Dangerous Star Map API interface module tests

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

NOTE: For these tests, it is advised to run pytest with the -W ignore::DeprecationWarning due to framework issues.
"""
import pytest
from src.packages.edsm import *


# Test System
# 1: Existing sys
@pytest.mark.asyncio
async def test_sys():
    sys = await GalaxySystem.get_info("Sol", CacheOverride=True)
    assert sys.name == "Sol"


# 2: Non-Existent Sys
@pytest.mark.asyncio
async def test_non_sys():
    sys = await GalaxySystem.get_info("Praisehalpydamnwhyisthisnotasysnam", CacheOverride=True)
    assert sys is None


# Test Sys Exists
# 1: Existing sys
@pytest.mark.asyncio
async def test_sys_exists():
    sysexists = await GalaxySystem.exists("Sol", CacheOverride=True)
    assert sysexists is True


# 2: Non-Existent Sys
@pytest.mark.asyncio
async def test_non_sys_exists():
    sysexists = await GalaxySystem.exists("Praisehalpydamnwhyisthisnotasysnam", CacheOverride=True)
    assert sysexists is False


# Test Nearby Systems
# 1: Existing Nearby
@pytest.mark.asyncio
async def test_sys_nearby():
    nearby_sys = await GalaxySystem.get_nearby('1', '2', '3')
    assert nearby_sys == ('Hixkar', 98.25)


# 2: Non-Existent Nearby
@pytest.mark.asyncio
async def test_sys_not_nearby():
    nearby_sys = await GalaxySystem.get_nearby('1000000000', '20000000000', '30000000000')
    assert nearby_sys == (None, None)


# Test CMDR
# 1: Existing CMDR
@pytest.mark.asyncio
async def test_cmdr():
    cmdr = await Commander.get_cmdr("Rixxan", CacheOverride=True)
    assert cmdr.name == "Rixxan"


# 2: Non-Existent CMDR
@pytest.mark.asyncio
async def test_noncmdr():
    cmdr = await Commander.get_cmdr("Praisehalpydamnwhyisthisnotacmdrnam", CacheOverride=True)
    assert cmdr is None


# CMDR Location
# This Module Cannot be pre-programmed. Be sure to test it yourself!
# CMDR Distance
# This Module Cannot be pre-programmed. Be sure to test it yourself!

# Landmarks
@pytest.mark.asyncio
async def test_landmark():
    landmark = await checklandmarks("Delkar", CacheOverride=True)
    assert landmark == ('Sol', '83.11', 'SW')


# DSSA
@pytest.mark.asyncio
async def test_dssa():
    dssa = await checkdssa("Col 285 Sector AA-A a30-2", CacheOverride=True)
    assert dssa == ('Synuefuae CM-J d10-42 (DSSA Artemis Rest)', '6,129.55', 'East')


# Calculate Distance
@pytest.mark.asyncio
async def test_coords():
    coords = await calc_distance(-1, 2, 3, 400, 500, 600)
    assert coords == 409.41


# Calculate Direction
@pytest.mark.asyncio
async def test_direction():
    direction = await calc_direction(-1, 2, 500, 600)
    assert direction == 'North'


# Calculate Direction
@pytest.mark.asyncio
async def test_nearby():
    nearby = await get_nearby_system("Sagittarius A*", CacheOverride=True)
    assert nearby == (True, 'Sagittarius A*')

# Calculate Direction
@pytest.mark.asyncio
async def test_distance():
    dist = await checkdistance("Sagittarius A*", "Delkar")
    assert dist == ('25,864.81', 'North')
