import pydle
import puresasl
import logging
import threading

from config import IRC, Logging, ChannelArray # This file is in the venv section for some reason. IDK.

logging.basicConfig(filename='rixshouldnotcode.log', level=logging.DEBUG) #should probably rename this.
pool = pydle.ClientPool()

# Simple echo bot.
class HalpyBOT(pydle.Client):
    async def on_connect(self):
        await super().on_connect()
        await self.raw(f"OPER {IRC.operline} {IRC.operlinePassword}\r\n")
        logging.info("Connected")
        await self.join("#bot-test") #Tried to make this an array, didn't work. TODO.

    # Start Completely UGLY way to respond to messages
    @pydle.coroutine
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
    @pydle.coroutine
    async def on_private_message(self, target, source, message):
        sender = source
        if message.startswith(IRC.commandPrefix):
            # don't respond to our own messages, as this leads to a positive feedback loop
            if source != self.nickname:
                await self.message(sender, "Command valid \n one \n two \n three \n four \n five \n six \n VII \n VIII \n IX \n X \n XI")
                await self.message(sender, "Command valid \n one \n two \n three \n four \n five \n six \n VII \n VIII \n IX \n X \n XI")
                await self.message(sender, "Command valid \n one \n two \n three \n four \n five \n six \n VII \n VIII \n IX \n X \n XI")

        else:  # REMOVE THIS OR IT WILL RESPOND TO EVERY MESSAGE
            if source != self.nickname:
                await self.message(sender, "Use command prefixes, dumbass")

    # End Completely UGLY way to respond to DMs
# End simple bastardized echo bot

# Ignore literally everything above, it can go die in a hole and was used for tests only.

client = HalpyBOT(
    IRC.nickname,
    sasl_identity = '', #Removed for Git Push
    sasl_password = '', #Removed for Git Push
    sasl_username = ''  #Removed for Git Push
)
pool.connect(client, IRC.server, IRC.port, tls=IRC.useSsl)
thread = threading.Thread(target=pool.handle_forever)
thread.start()
