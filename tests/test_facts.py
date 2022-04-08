"""
HalpyBOT v1.6

test_facts.py - Fact handler tests

Copyright (c) 2022 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

NOTE: For these tests, it is advised to run pytest with the -W ignore::DeprecationWarning due to framework issues.
"""
import pytest
from halpybot.packages.command import Commands
from halpybot.packages.configmanager import config


@pytest.mark.asyncio
async def test_pcfr(bot_fx):
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
