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


@pytest.mark.asyncio
async def test_serverping(bot_fx):
    await Commands.invoke_from_message(
        bot=bot_fx, channel="#bot-test", sender="generic_seal", message=f"{config['IRC']['commandprefix']}ping"
    )
    assert bot_fx.sent_messages[0] == {"message": "Pong!", "target": "#bot-test"}
