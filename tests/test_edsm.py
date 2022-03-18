"""
HalpyBOT v1.5.2

test_edsm.py - Elite: Dangerous Star Map API interface module tests

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

NOTE: For these tests, it is advised to run pytest with the -W ignore::DeprecationWarning due to framework issues.
"""
import pytest
import aiohttp
import asyncio

import halpybot.packages.edsm.edsm
from halpybot.packages.edsm import *
from unittest.mock import patch


@pytest.fixture
def event_loop():
    yield asyncio.get_event_loop()


def pytest_sessionfinish(session, exitstatus):
    asyncio.get_event_loop().close()


# Test System
# 1: Existing sys
@pytest.mark.asyncio
async def test_sys():
    sys = await GalaxySystem.get_info("Sol", cache_override=True)
    assert sys.name == "Sol"


# 2: Non-Existent Sys
@pytest.mark.asyncio
async def test_non_sys():
    sys = await GalaxySystem.get_info(
        "Praisehalpydamnwhyisthisnotasysnam", cache_override=True
    )
    assert sys is None


# 3: GetInfo error
@pytest.mark.asyncio
async def test_request_error():
    with patch(
        "halpybot.packages.edsm.GalaxySystem.get_info",
        side_effect=aiohttp.ClientError("Err"),
    ):
        with pytest.raises(aiohttp.ClientError):
            await GalaxySystem.get_info(
                "Praisehalpydamnwhyisthisnotasysnam", cache_override=True
            )


# Test Sys Exists
# 1: Existing sys
@pytest.mark.asyncio
async def test_sys_exists():
    sysexists = await GalaxySystem.exists("Sol", cache_override=True)
    assert sysexists is True


# 2: Non-Existent Sys
@pytest.mark.asyncio
async def test_non_sys_exists():
    sysexists = await GalaxySystem.exists(
        "Praisehalpydamnwhyisthisnotasysnam", cache_override=True
    )
    assert sysexists is False


# Test Nearby Systems
# 1: Existing Nearby
@pytest.mark.asyncio
async def test_sys_nearby():
    nearby_sys = await GalaxySystem.get_nearby("1", "2", "3")
    assert nearby_sys == ("Hixkar", 98.25)


# 2: Non-Existent Nearby
@pytest.mark.asyncio
async def test_sys_not_nearby():
    nearby_sys = await GalaxySystem.get_nearby(
        "1000000000", "20000000000", "30000000000"
    )
    assert nearby_sys == (None, None)


# 3: GetNearby error
@pytest.mark.asyncio
async def test_request_nearby_error():
    with patch(
        "halpybot.packages.edsm.GalaxySystem.get_nearby",
        side_effect=aiohttp.ClientError("Err"),
    ):
        with pytest.raises(aiohttp.ClientError):
            await GalaxySystem.get_nearby("1", "2", "3")


# Test CMDR
# 1: Existing CMDR
@pytest.mark.asyncio
async def test_cmdr():
    cmdr = await Commander.get_cmdr("Rixxan", cache_override=True)
    assert cmdr.name == "Rixxan"


# 2: Non-Existent CMDR
@pytest.mark.asyncio
async def test_noncmdr():
    cmdr = await Commander.get_cmdr(
        "Praisehalpydamnwhyisthisnotacmdrnam", cache_override=True
    )
    assert cmdr is None


# 2: Cached CMDR
@pytest.mark.asyncio
async def test_noncmdr2():
    cmdr = await Commander.get_cmdr("Rixxan")
    assert cmdr.name == "Rixxan"
    cmdr = await Commander.get_cmdr("Rixxan")
    assert cmdr.name == "Rixxan"


# CMDR Location - As this can be dynamic, we will simply assume any response is valid.
@pytest.mark.asyncio
async def test_location():
    location = await Commander.location("Rixxan")
    assert location is not None


# Landmarks
@pytest.mark.asyncio
async def test_landmark():
    landmark = await checklandmarks("Delkar", cache_override=True)
    assert landmark == ("Sol", "83.11", "SW")


@pytest.mark.asyncio
async def test_distance_bad_landmark():
    with pytest.raises(NoResultsEDSM):
        await checklandmarks("Sagittarius B*")


# DSSA
@pytest.mark.asyncio
async def test_dssa():
    dssa = await checkdssa("Col 285 Sector AA-A a30-2", cache_override=True)
    assert dssa == ("Synuefuae CM-J d10-42 (DSSA Artemis Rest)", "6,129.55", "East")


@pytest.mark.asyncio
async def test_distance_bad_dssa():
    with pytest.raises(NoResultsEDSM):
        await checkdssa("Sagittarius B*")


# Calculate Distance
def test_coords():
    coords = calc_distance(-1, 2, 3, 400, 500, 600)
    assert coords == 409.41


# Calculate Direction
@pytest.mark.asyncio
async def test_direction():
    direction = await calc_direction(-1, 2, 500, 600)
    assert direction == "North"


# Calculate Direction
@pytest.mark.asyncio
async def test_nearby():
    nearby = await get_nearby_system("Sagittarius A*", cache_override=True)
    assert nearby == (True, "Sagittarius A*")


@pytest.mark.asyncio
async def test_nearby_extra():
    nearby = await get_nearby_system("Delkar 3 a", cache_override=True)
    assert nearby == (True, "Delkar")


# Calculate Direction
@pytest.mark.asyncio
async def test_distance():
    dist = await checkdistance("Sagittarius A*", "Delkar")
    assert dist == ("25,864.81", "North")


@pytest.mark.asyncio
async def test_distance_no_a():
    with pytest.raises(EDSMConnectionError):
        await checkdistance("", "Delkar")
        await checkdistance("Delkar", "")


@pytest.mark.asyncio
async def test_distance_bad_sys():
    with pytest.raises(NoResultsEDSM):
        await checkdistance("Sagittarius B*", "ThisCMDRDoesntExist")


@pytest.mark.asyncio
async def test_distance_bad_sys_2():
    with pytest.raises(NoResultsEDSM):
        await checkdistance("Sagittarius A*", "ThisCMDRStillDoesntExist")


@pytest.mark.asyncio
async def test_distance_with_cmdr():
    dist = await checkdistance("Rixxan", "Delkar")
    dist2 = await checkdistance("Delkar", "Rixxan")
    assert dist[0] == dist2[0]


@pytest.mark.asyncio
async def test_distance_cmdr_coords():
    cmdr = await halpybot.packages.edsm.edsm.get_coordinates("Rixxan")
    assert cmdr is not None


@pytest.mark.asyncio
async def test_distance_bad_cleaner():
    not_procgen = await sys_cleaner("lp 732-94")
    assert not_procgen == "LP 732-94"


@pytest.mark.asyncio
async def test_distance_check_landmarks_far():
    with pytest.raises(NoResultsEDSM):
        await checklandmarks("Skaudoae UF-Q b47-1")
