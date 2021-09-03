from src.packages.edsm import *
import pytest

# TODO Yes this still needs a lot of work

@pytest.mark.asyncio
async def test_get_system():
    system = await GalaxySystem.get_info(name="Sol")
    assert system.name == "Sol"
    assert system.coords == {"x": 0, "y": 0, "z": 0}

@pytest.mark.asyncio
async def test_nonexistent_sys():
    system = await GalaxySystem.get_info("Praisehalpydamnwhyisthisnotasystemname")
    assert system is None

@pytest.mark.asyncio
async def test_commander():
    cmdr = await Commander.get_cmdr(name="Rik079")
    assert cmdr.name == "Rik079"

@pytest.mark.asyncio
async def test_nonexistent_commander():
    cmdr = await Commander.get_cmdr(name="Praisehalpydamnwhyisthisnotasystemnam")
    assert cmdr is None
