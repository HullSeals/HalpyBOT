import pydle
import logging
import threading
import modules.commandhandler as commandhandler

from config import IRC, ChannelArray, SASL

logging.basicConfig(filename='halpybot.log', level=logging.DEBUG)
pool = pydle.ClientPool()

class HalpyBOT(pydle.Client):
    # Join the Server and Channels and OperLine
    async def on_connect(self):
        await super().on_connect()
        await self.raw(f"OPER {IRC.operline} {IRC.operlinePassword}\r\n")
        logging.info("Connected")
        print("Connected!")
        for channel in ChannelArray.channels:
            await self.join(channel)

    @pydle.coroutine
    async def on_channel_message(self, target, nick, message):
        await super().on_channel_message(target, nick, message)
        await commandhandler.on_channel_message(self, target, nick, message)


# Define the Client, mostly pulled from config.py
client = HalpyBOT(
    IRC.nickname,
    sasl_identity=SASL.identity,
    sasl_password=SASL.password,
    sasl_username=SASL.username
)
try:
    pool.connect(client, IRC.server, IRC.port, tls=IRC.useSsl)
    thread = threading.Thread(target=pool.handle_forever)
    thread.start()
except pydle.Error as error:
    print(f"Unable to connect: {error}")
