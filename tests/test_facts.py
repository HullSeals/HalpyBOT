"""
HalpyBOT v1.6

test_facts.py - Fact handler tests

Copyright (c) 2022 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

NOTE: For these tests, it is advised to run pytest with the -W ignore::DeprecationWarning due to framework issues.

Testing will always DISABLE offline mode. You must have access to a Seal-type DB for testing.
"""
import pytest
from halpybot.packages.command import Commands
from halpybot.packages.configmanager import config, config_write


@pytest.mark.asyncio
async def test_pcfr(bot_fx):
    """Test if the PCFR fact can be sent from the backup file"""
    await Commands.invoke_from_message(
        bot=bot_fx,
        channel="#bot-test",
        sender="some_pup",
        message=f"{config['IRC']['commandprefix']}pcfr",
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
        message=f"{config['IRC']['commandprefix']}factinfo pcfr",
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
        message=f"{config['IRC']['commandprefix']}factinfo pcfr",
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
        message=f"{config['IRC']['commandprefix']}allfacts",
    )
    assert bot_fx.sent_messages[0].get("message").startswith("All English facts:")


@pytest.mark.asyncio
async def test_allfacts_2(bot_fx):
    """Test the allfacts command in Dutch"""
    await Commands.invoke_from_message(
        bot=bot_fx,
        channel="generic_seal",
        sender="generic_seal",
        message=f"{config['IRC']['commandprefix']}allfacts nl",
    )
    assert bot_fx.sent_messages[0] == {
        "message": "All Dutch facts:\npcfr",
        "target": "generic_seal",
    }


@pytest.mark.asyncio
async def test_ufi(bot_fx):
    """Test the UFI Command"""
    if config["Offline Mode"]["enabled"] == "True":
        pytest.skip("Offline Mode Enabled")
    prev_value = config["Offline Mode"]["enabled"]
    config_write("Offline Mode", "enabled", "False")

    await Commands.invoke_from_message(
        bot=bot_fx,
        channel="some_cyber",
        sender="some_cyber",
        message=f"{config['IRC']['commandprefix']}ufi",
    )
    assert bot_fx.sent_messages[0] == {
        "message": "Fact cache updated.",
        "target": "some_cyber",
    }
    config_write("Offline Mode", "enabled", prev_value)
