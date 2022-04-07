import pytest
from halpybot.packages.command import Commands, CommandGroup


@pytest.mark.asyncio
async def test_serverping(bot_fx):
    # await Commands.invoke_from_message(
    #     bot=bot_fx,
    #     channel="#bot-test",
    #     sender="generic_seal",
    #     message="^ping"
    # )
    await Commands.invoke_command(
        command="ping",
        command_context=bot_fx,
        arguments=[]
    )
    assert bot_fx.sent_messages[0] == "Pong!"
