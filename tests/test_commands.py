"""
HalpyBOT v1.6

test_commands.py - What are your orders, Captain?

Copyright (c) 2022 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
import pytest
from halpybot.packages.command import Commands
from halpybot.packages.configmanager import config

# noinspection PyUnresolvedReferences
from .mock_edsm import mock_api_server_fx


@pytest.mark.asyncio
async def test_serverping(bot_fx):
    await Commands.invoke_from_message(
        bot=bot_fx,
        channel="#bot-test",
        sender="generic_seal",
        message=f"{config['IRC']['commandprefix']}ping",
    )
    assert bot_fx.sent_messages[0] == {"message": "Pong!", "target": "#bot-test"}


@pytest.mark.asyncio
async def test_lookup(bot_fx, mock_api_server_fx):
    await Commands.invoke_from_message(
        bot=bot_fx,
        channel="#bot-test",
        sender="generic_seal",
        message=f"{config['IRC']['commandprefix']}lookup Sol",
    )
    assert bot_fx.sent_messages[0] == {
        "message": "System SOL exists in EDSM",
        "target": "#bot-test",
    }


@pytest.mark.asyncio
async def test_lookup_2(bot_fx, mock_api_server_fx):
    await Commands.invoke_from_message(
        bot=bot_fx,
        channel="#bot-test",
        sender="generic_seal",
        message=f"{config['IRC']['commandprefix']}lookup",
    )
    assert bot_fx.sent_messages[0] == {
        "message": "Use: ^lookup [System Name]\nAliases: syslookup\nCheck if a system exists in EDSM",
        "target": "#bot-test",
    }


@pytest.mark.asyncio
async def test_lookup_3(bot_fx, mock_api_server_fx):
    await Commands.invoke_from_message(
        bot=bot_fx,
        channel="#bot-test",
        sender="generic_seal",
        message=f"{config['IRC']['commandprefix']}lookup PRAISEHALPYDAMNWHYISTHISNOTASYSNAM",
    )
    assert bot_fx.sent_messages[0] == {
        "message": "System PRAISEHALPYDAMNWHYISTHISNOTASYSNAM not found in EDSM",
        "target": "#bot-test",
    }


@pytest.mark.asyncio
async def test_lookup_4(bot_fx, mock_api_server_fx):
    await Commands.invoke_from_message(
        bot=bot_fx,
        channel="#bot-test",
        sender="generic_seal",
        message=f"{config['IRC']['commandprefix']}lookup --new Sol",
    )
    assert bot_fx.sent_messages[0] == {
        "message": "System SOL exists in EDSM",
        "target": "#bot-test",
    }


@pytest.mark.asyncio
async def test_drillcase(bot_fx):
    await Commands.invoke_from_message(
        bot=bot_fx,
        channel="#bot-test",
        sender="generic_seal",
        message=f"{config['IRC']['commandprefix']}drillcase Rixxan, PC, Delkar, 90",
    )
    assert bot_fx.sent_messages[0] == {
        "message": "xxxx DRILL -- DRILL -- DRILL xxxx\nCMDR: Rixxan -- Platform: PC\nSystem: DELKAR -- Hull: 90\nxxxxxxxx",
        "target": "#bot-test",
    }


@pytest.mark.asyncio
async def test_drillcase_unauth(bot_fx):
    await Commands.invoke_from_message(
        bot=bot_fx,
        channel="#bot-test",
        sender="some_pup",
        message=f"{config['IRC']['commandprefix']}drillcase Rixxan, PC, Delkar, 90",
    )
    assert bot_fx.sent_messages[0] == {
        "message": "You have to be a drilled seal to use this!",
        "target": "#bot-test",
    }


@pytest.mark.asyncio
async def test_drillcase_unauth_guest(bot_fx):
    await Commands.invoke_from_message(
        bot=bot_fx,
        channel="#bot-test",
        sender="guest_user",
        message=f"{config['IRC']['commandprefix']}drillcase Rixxan, PC, Delkar, 90",
    )
    assert bot_fx.sent_messages[0] == {
        "message": "You have to be a drilled seal to use this!",
        "target": "#bot-test",
    }


@pytest.mark.asyncio
async def test_help(bot_fx):
    await Commands.invoke_from_message(
        bot=bot_fx,
        channel="#bot-test",
        sender="guest_user",
        message=f"{config['IRC']['commandprefix']}help",
    )
    assert bot_fx.sent_messages[0] == {
        "message": "Responding in DMs!",
        "target": "#bot-test",
    }
    assert bot_fx.sent_messages[1].get("target") == "guest_user"
    assert bot_fx.sent_messages[1].get("message") is not False


@pytest.mark.asyncio
async def test_say_channel(bot_fx):
    await Commands.invoke_from_message(
        bot=bot_fx,
        channel="#bot-test",
        sender="some_user",
        message=f"{config['IRC']['commandprefix']}say #bot-test bacon and eggs",
    )
    assert bot_fx.sent_messages[0] == {
        "message": "Responding in DMs!",
        "target": "#bot-test",
    }
    assert bot_fx.sent_messages[1] == {
        "message": "You have to run that command in DMs with me!",
        "target": "some_user",
    }