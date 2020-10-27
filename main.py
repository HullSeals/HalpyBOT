import pydle
import logging
import modules.commandhandler as commandhandler
import asyncio

from config import IRC, ChannelArray, SASL

logging.basicConfig(filename='halpybot.log', level=logging.DEBUG)

class HalpyBOT(pydle.Client):
    # Join the Server and Channels and OperLine
    async def on_connect(self):
        await super().on_connect()
        await self.raw(f"OPER {IRC.operline} {IRC.operlinePassword}\r\n")
        logging.info("Connected")
        print("Connected!")
        for channel in ChannelArray.channels:
            await self.join(channel)
            logging.info(channel)

    async def on_channel_message(self, target, nick, message):
        await super().on_channel_message(target, nick, message)
        await commandhandler.on_channel_message(self, target, nick, message)

    async def on_private_message(self, target, nick, message):
        await super().on_private_message(target, nick, message)
        await commandhandler.on_private_message(self, target, nick, message)


# Define the Client, mostly pulled from config.py
client = HalpyBOT(
    IRC.nickname,
    sasl_identity=SASL.identity,
    sasl_password=SASL.password,
    sasl_username=SASL.username
)

async def start():
    await client.connect(IRC.server, IRC.port, tls=IRC.useSsl, tls_verify=False)

if __name__ == "__main__":
    LOOP = asyncio.get_event_loop()
    LOOP.run_until_complete(start())
    LOOP.run_forever()
