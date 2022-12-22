"""
test_edsm.py - Elite: Dangerous Star Map API interface module tests

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from unittest.mock import patch
import pytest
import aiohttp
from halpybot.packages.configmanager import config
import halpybot.packages.edsm.edsm
from halpybot.packages.edsm import (
    GalaxySystem,
    Commander,
    checkdistance,
    checkdssa,
    checklandmarks,
    NoResultsEDSM,
    calc_distance,
    calc_direction,
    get_nearby_system,
    EDSMConnectionError,
    sys_cleaner,
    NoNearbyEDSM,
    EDSMReturnError,
)

# noinspection PyUnresolvedReferences
from .fixtures.mock_edsm import mock_api_server_fx

SAFE_IP = "http://127.0.0.1:4000"
CONFIG_IP = config.edsm.uri
GOOD_IP = False

if CONFIG_IP == SAFE_IP:
    GOOD_IP = True

pytestmark = pytest.mark.skipif(
    GOOD_IP is not True, reason="Invalid EDSM IP in Config. Please update to continue."
)


# Test System
# 1: Existing sys
@pytest.mark.asyncio
async def test_sys(mock_api_server_fx):
    """Test that EDSM returns a valid response for a given system"""
    sys = await GalaxySystem.get_info("Sol", cache_override=True)
    assert sys.name == "Sol"


# 2: Non-Existent Sys
@pytest.mark.asyncio
async def test_non_sys():
    """Test that an invalid system does not return a good value."""
    sys = await GalaxySystem.get_info(
        "Praisehalpydamnwhyisthisnotasysnam", cache_override=True
    )
    assert sys is None


# 3: GetInfo error
@pytest.mark.asyncio
async def test_request_error():
    """Test that the module will error correctly if EDSM doesn't respond"""
    with patch(
        "halpybot.packages.edsm.GalaxySystem.get_info",
        side_effect=aiohttp.ClientError("Err"),
    ):
        with pytest.raises(aiohttp.ClientError):
            await GalaxySystem.get_info(
                "Praisehalpydamnwhyisthisnotasysnam", cache_override=True
            )


@pytest.mark.asyncio
async def test_sys_nearby():
    """Test that we can get a nearby system name from a given set of coordinates"""
    nearby_sys = await GalaxySystem.get_nearby("1", "2", "3")
    assert nearby_sys == ("Hixkar", 98.25)


@pytest.mark.asyncio
async def test_sys_not_nearby():
    """Test that impossible coordinates will return None systems nearby"""
    nearby_sys = await GalaxySystem.get_nearby(
        "1000000000", "20000000000", "30000000000"
    )
    assert nearby_sys == (None, None)


@pytest.mark.asyncio
async def test_request_nearby_error():
    """Test that the module will error correctly if EDSM doesn't respond"""
    with patch(
        "halpybot.packages.edsm.GalaxySystem.get_nearby",
        side_effect=aiohttp.ClientError("Err"),
    ):
        with pytest.raises(aiohttp.ClientError):
            await GalaxySystem.get_nearby("1", "2", "3")


@pytest.mark.asyncio
async def test_cmdr():
    """Test that EDSM returns a valid response for a given CMDR"""
    cmdr = await Commander.get_cmdr("Rixxan", cache_override=True)
    assert cmdr.name == "Rixxan"


@pytest.mark.asyncio
async def test_noncmdr():
    """Test that EDSM will return a None value for a bad CMDR Name"""
    cmdr = await Commander.get_cmdr(
        "Praisehalpydamnwhyisthisnotacmdrnam", cache_override=True
    )
    assert cmdr is None


@pytest.mark.asyncio
async def test_noncmdr2():
    """Test that the caching system responds correctly on a repeated value"""
    cmdr = await Commander.get_cmdr("Rixxan")
    assert cmdr.name == "Rixxan"
    cmdr = await Commander.get_cmdr("Rixxan")
    assert cmdr.name == "Rixxan"


@pytest.mark.asyncio
async def test_location():
    """Test that the Commander system responds with a value"""
    location = await Commander.location("Rixxan")
    assert location.system == "Pleiades Sector HR-W d1-79"


@pytest.mark.asyncio
async def test_location_malformed():
    """Test that the Commander system can process a malformed EDSM return"""
    with pytest.raises(EDSMReturnError):
        await Commander.location("Abildgaard Jadrake")


@pytest.mark.asyncio
async def test_landmark():
    """Test that the Landmark system operates correctly"""
    landmark = await checklandmarks("Delkar", cache_override=True)
    assert landmark == ("Sol", "83.11", "SW")


@pytest.mark.asyncio
async def test_distance_bad_landmark():
    """Test that the Landmark system will return the proper exception to a bad system"""
    with pytest.raises(NoResultsEDSM):
        await checklandmarks("Sagittarius B*")


@pytest.mark.asyncio
async def test_dssa():
    """Test that the DSSA system operates correctly"""
    dssa = await checkdssa("Col 285 Sector AA-A a30-2", cache_override=True)
    assert dssa == ("Synuefuae CM-J d10-42 (DSSA Artemis Rest)", "6,129.55", "East")


@pytest.mark.asyncio
async def test_distance_bad_dssa():
    """Test that the DSSA system will return the proper exception to a bad system"""
    with pytest.raises(NoResultsEDSM):
        await checkdssa("Sagittarius B*")


def test_coords():
    """Test that the distance calculator responds the proper distance"""
    coords = calc_distance(-1, 2, 3, 400, 500, 600)
    assert coords == 409.41


@pytest.mark.asyncio
async def test_direction():
    """Test that the direction calculator responds with the proper direction"""
    direction = await calc_direction(-1, 2, 500, 600)
    assert direction == "North"


@pytest.mark.asyncio
async def test_nearby():
    """Test that a system will respond properly if fed itself"""
    nearby = await get_nearby_system("Sagittarius A*")
    assert nearby == (True, "Sagittarius A*")


@pytest.mark.asyncio
async def test_nearby_extra():
    """Test that the system cleaner will properly if fed extra details (to a point)"""
    nearby = await get_nearby_system("Delkar 3 a")
    assert nearby == (True, "Delkar")


@pytest.mark.asyncio
async def test_distance():
    """Test that the distance system will calculate properly"""
    dist = await checkdistance("Sagittarius A*", "Delkar")
    assert dist == ("25,864.81", "North")


@pytest.mark.asyncio
async def test_distance_no_a():
    """Test that null arguments will error properly"""
    with pytest.raises(EDSMConnectionError):
        await checkdistance("", "Delkar")
        await checkdistance("Delkar", "")


@pytest.mark.asyncio
async def test_distance_bad_sys():
    """Test that distances between non-existing points will error properly"""
    with pytest.raises(NoResultsEDSM):
        await checkdistance("Sagittarius B*", "ThisCMDRDoesntExist")


@pytest.mark.asyncio
async def test_distance_bad_sys_2():
    """Test that distances between only one incorrect point will error properly"""
    with pytest.raises(NoResultsEDSM):
        await checkdistance("Sagittarius A*", "ThisCMDRDoesntExist")


@pytest.mark.asyncio
async def test_distance_with_cmdr():
    """Test that Distances will respond properly both ways"""
    dist = await checkdistance("Rixxan", "Delkar")
    dist2 = await checkdistance("Delkar", "Rixxan")
    assert dist[0] == dist2[0]


@pytest.mark.asyncio
async def test_distance_cmdr_coords():
    """Check that the independent get_coordinates system works"""
    cmdr = await halpybot.packages.edsm.edsm.get_coordinates("Rixxan")
    assert cmdr is not None


@pytest.mark.asyncio
async def test_sys_cleaner():
    """Test that the system cleaner works properly with nonprocgen"""
    not_procgen = await sys_cleaner("lp 732-94")
    assert not_procgen == "LP 732-94"


@pytest.mark.asyncio
async def test_cleaner_2():
    """ "Test the system cleaner works with procGen"""
    not_procgen = await sys_cleaner("Col 285 Sector HN-I c1O-19")
    assert not_procgen == "COL 285 SECTOR HN-I C10-19"


@pytest.mark.asyncio
async def test_distance_check_landmarks_far():
    """Test a distant system doesn't have a landmark within range"""
    with pytest.raises(NoNearbyEDSM):
        await checklandmarks("Skaudoae UF-Q b47-1")
