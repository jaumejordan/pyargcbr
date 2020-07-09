import time

from loguru import logger
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message

from .protocol import REGISTER_PROTOCOL, REQUEST_PROTOCOL, \
    ACCEPT_PERF, REQUEST_PERF, LAST_MODIFICATION_DATE_PERF, PROTOCOL, PERFORMATIVE, MessageCodification


class DebugAgent(Agent):
    class KKBehaviour(CyclicBehaviour):
        def __init__(self):
            super().__init__()
            self.accepted = False

        async def on_start(self):
            time.sleep(3)
            logger.info("Starting kk_behaviour . . .")

        async def ask_last_modification_date(self):
            logger.info("Asking for last modification date")
            request = Message()
            request.to = "commitment_store@localhost"
            request.set_metadata(PROTOCOL, REQUEST_PROTOCOL)
            request.set_metadata(PERFORMATIVE, LAST_MODIFICATION_DATE_PERF)
            await self.send(request)
            msg = await self.receive(timeout=5)
            if msg:
                return MessageCodification.get_decoded_message_content(msg)
            else:
                return None

        async def ask_for_registration(self):
            logger.info("Asking for registration")
            request = Message()
            request.to = "commitment_store@localhost"
            request.set_metadata(PROTOCOL, REGISTER_PROTOCOL)
            request.set_metadata(PERFORMATIVE, REQUEST_PERF)
            await self.send(request)
            msg = await self.receive(timeout=5)
            if msg:
                if msg.get_metadata(PERFORMATIVE) == ACCEPT_PERF:
                    logger.success("YAHOO! I have been accepted and registered!")
                    self.accepted = True
                else:
                    logger.error("YIKES! I have been regret")

        async def run(self):
            if not self.accepted:
                await self.ask_for_registration()
            else:
                date = await self.ask_last_modification_date()
                if date:
                    logger.info("The millis is: {}".format(date))
                else:
                    logger.error("FAIL")
                await self.agent.stop()

    async def setup(self):
        logger.info("Agent starting . . .")
        b = self.KKBehaviour()
        self.add_behaviour(b)
