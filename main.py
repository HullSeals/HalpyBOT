import pydle
import logging
import threading

from config import IRC, ChannelArray, SASL

logging.basicConfig(filename='halpybot.log', level=logging.DEBUG)
pool = pydle.ClientPool()

# Simple echo bot.

class HalpyBOT(pydle.Client):
    # Join the Server and Channels and OperLine
    async def on_connect(self):
        await super().on_connect()
        await self.raw(f"OPER {IRC.operline} {IRC.operlinePassword}\r\n")
        logging.info("Connected")
        print("Connected!")
        for channel in ChannelArray.channels:
            await self.join(channel)
#To Be Removed
    # Start Completely UGLY way to respond to messages
    async def on_message(self, target, source, message):
        if message.startswith(IRC.commandPrefix):
            # don't respond to our own messages, as this leads to a positive feedback loop
            if source != self.nickname:
                await self.message(target, "Command valid")
        else:  # REMOVE THIS OR IT WILL RESPOND TO EVERY BASTARD ON THE SERVER
            if source != self.nickname:
                await self.message(target, "Use command prefixes, dumbass")
    # End Completely UGLY way to respond to messages

    # Start Completely UGLY way to respond to DMs
    async def on_private_message(self, source, message):
        sender = source
        if message.startswith(IRC.commandPrefix):
            # don't respond to our own messages, as this leads to a positive feedback loop
            if source != self.nickname:
                await self.message(sender, "Command valid \n one \n two \n three \n"
                                           " four \n five \n six \n VII \n VIII \n IX \n X \n XI")
                await self.message(sender, "Command valid \n one \n two \n three \n"
                                           " four \n five \n six \n VII \n VIII \n IX \n X \n XI")
                await self.message(sender, "Command valid \n one \n two \n three \n"
                                           " four \n five \n six \n VII \n VIII \n IX \n X \n XI")

        else:  # REMOVE THIS OR IT WILL RESPOND TO EVERY MESSAGE
            if source != self.nickname:
                await self.message(sender, "Use command prefixes, dumbass")

    # End Completely UGLY way to respond to DMs
# End To Be Removed

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
