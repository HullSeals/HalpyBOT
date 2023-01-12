"""
test_facts.py - Fact handler tests

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

Testing will always DISABLE offline mode. You must have access to a Seal-type DB for testing.
"""
import pytest
from halpybot.packages.command import Commands
from halpybot import config


@pytest.mark.asyncio
async def test_pcfr(bot_fx):
    """Test if the PCFR fact can be sent from the backup file"""
    await Commands.invoke_from_message(
        bot=bot_fx,
        channel="#bot-test",
        sender="some_pup",
        message=f"{config.irc.command_prefix}pcfr",
    )
    assert bot_fx.sent_messages[0] == {
        "message": "Please tap ESC to go to the PAUSE menu, click SOCIAL, enter the CMDR name in the box, and click ADD FRIEND on their name.",
        "target": "#bot-test",
    }


@pytest.mark.asyncio
async def test_factinfo(bot_fx):
    """Test the factinfo command"""
    await Commands.invoke_from_message(
        bot=bot_fx,
        channel="#bot-test",
        sender="some_cyber",
        message=f"{config.irc.command_prefix}factinfo pcfr",
    )
    assert bot_fx.sent_messages[1] == {
        "message": "Fact: pcfr\n"
        "Language: English (EN)\n"
        "All langs: English (EN), Dutch (NL)\n"
        "ID: None\n"
        "Author: OFFLINE\n"
        "Text: Please tap ESC to go to the PAUSE menu, click SOCIAL, enter "
        "the CMDR name in the box, and click ADD FRIEND on their name.",
        "target": "some_cyber",
    }


@pytest.mark.asyncio
async def test_factinfo_2(bot_fx):
    """Test the factinfo command with an unauthorized user"""
    await Commands.invoke_from_message(
        bot=bot_fx,
        channel="#bot-test",
        sender="generic_seal",
        message=f"{config.irc.command_prefix}factinfo pcfr",
    )
    assert bot_fx.sent_messages[0] == {
        "message": "Only moderators+ can use this.",
        "target": "#bot-test",
    }


@pytest.mark.asyncio
async def test_allfacts(bot_fx):
    """Test the allfacts command"""
    await Commands.invoke_from_message(
        bot=bot_fx,
        channel="generic_seal",
        sender="generic_seal",
        message=f"{config.irc.command_prefix}allfacts",
    )
    assert bot_fx.sent_messages[0].get("message").startswith("All English facts:")


@pytest.mark.asyncio
async def test_allfacts_2(bot_fx):
    """Test the allfacts command in Dutch"""
    await Commands.invoke_from_message(
        bot=bot_fx,
        channel="generic_seal",
        sender="generic_seal",
        message=f"{config.irc.command_prefix}allfacts nl",
    )
    assert bot_fx.sent_messages[0] == {
        "message": "All Dutch facts:\npcfr",
        "target": "generic_seal",
    }

# FIXME: Rework for Inbuilt Tests
# @pytest.mark.asyncio
# async def test_ufi(bot_fx):
#     """Test the UFI Command"""
#     if config.offline_mode.enabled:
#         pytest.skip("Offline Mode Enabled")
#     prev_value = config.offline_mode.enabled
#     config.offline_mode.enabled = False
#
#     await Commands.invoke_from_message(
#         bot=bot_fx,
#         channel="some_cyber",
#         sender="some_cyber",
#         message=f"{config.irc.command_prefix}ufi",
#     )
#     assert bot_fx.sent_messages[0] == {
#         "message": "Fact cache updated.",
#         "target": "some_cyber",
#     }
#     config.offline_mode.enabled = prev_value
