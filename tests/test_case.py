"""
test_case.py - Case Module Tests

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import pytest

from halpybot import config
from halpybot.packages.command import Commands
from tests.fixtures.mock_board import mock_full_board_fx


@pytest.mark.asyncio
async def test_case_list(bot_fx):
    """Test the GO command"""
    await mock_full_board_fx(bot_fx)
    await bot_fx.facts._from_local()
    await Commands.invoke_from_message(
        bot=bot_fx,
        channel="#bot-test",
        sender="generic_seal",
        message=f"{config.irc.command_prefix}listcase 1",
    )
    print(bot_fx.sent_messages[1])
    assert bot_fx.sent_messages[1].get("target") == "generic_seal"
    assert (
        bot_fx.sent_messages[1]
        .get("message")
        .startswith(
            "Here's the self listing for Case ID 1:\n"
            " General Details: \n   Client: one\n   System: Delkar\n"
            "   Platform: ODYSSEY\n   Case Created:"
        )
    )
    assert (
        bot_fx.sent_messages[1]
        .get("message")
        .endswith(
            "Case Status: ACTIVE\n"
            "   Client Welcomed: No\nCode Black Details:\n   "
            "Hull Remaining: None\n   Canopy Status: Intact\n   "
            "O2 Reported Time: None\n   Synths Available: No\nResponder "
            "Details:\n   Dispatchers: None Yet!\n   Responders: None Yet!\n"
            "   Notes: \n      None Yet!"
        )
    )
