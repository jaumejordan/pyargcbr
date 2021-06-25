from time import sleep
from datetime import datetime
from typing import List, Optional

from loguru import logger
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message

from pyargcbr.agents.arg_message import ArgMessage, create_message


from pyargcbr.agents.argumentation_agent import ArgAgent
from pyargcbr.agents.protocol import ADD_DIALOGUE_PERF
from pyargcbr.knowledge_resources.dialogue import Dialogue
from pyargcbr.knowledge_resources.domain_case import DomainCase
from pyargcbr.knowledge_resources.social_entity import SocialEntity


class TestTriggerAgent(Agent):
    """This class represents a tester agent in charge of sending the test domain-case to solve to a group
    of agents and acts as the initiator of the dialogue

    """

    def __init__(self, jid: str, password: str, social_entities: List[SocialEntity], commitment_store_id: str,
                 finish_filename: str, domain_cases: List[DomainCase], agents: List[ArgAgent],
                 multiplier_time_factor: int = 10, verify_security: bool = False):
        super().__init__(jid, password, verify_security)
        logger.info("{}: TestTriggerAgent created")

        self.my_id = jid
        self.social_entities = social_entities
        self.commitment_store_id = commitment_store_id
        self.finish_filename = finish_filename
        self.domain_cases = domain_cases
        self.agents = agents

        self.dialogue_init_time = 0
        self.multiplier_time_factor = multiplier_time_factor

    def finalize(self):  # TODO
        pass


class TestTriggerBehaviour(CyclicBehaviour):
    agent: TestTriggerAgent

    async def send(self, msg: ArgMessage):
        for receiver in msg.to:  # TODO Is this the way to do it?
            yield await super().send(Message(to=receiver, sender=msg.sender, metadata=msg.metadata, body=msg.body))

    def __init__(self):
        super().__init__()

    async def on_start(self):
        logger.info("Starting TestTriggerBehaviour of {}".format(self.agent.my_id))

    async def run(self):
        # Create the file where the results will be stored
        try:
            open(self.agent.finish_filename, "xb")
        except (FileExistsError, FileNotFoundError) as e:
            logger.exception("ERROR CREATING FINISH FILE:\n{}".format(e))
        # Waits 2 seconds at the beginning to let the other agent get full started
        try:
            sleep(2)
        except (InterruptedError, KeyboardInterrupt) as e:
            logger.exception("TestTriggerBehaviour interrupted during waiting time:\n{}".format(e))

        # create a new instance of the domain-case without the solutions, to act as a new problem to solve
        n_domain_case = 0
        aux_domain_case = self.agent.domain_cases[n_domain_case]
        domain_case2send = aux_domain_case

        # The dialogue that will represent the tested conversation
        time = datetime.now().microsecond
        current_dialogue_id = str(time)
        agent_ids: List[str] = []
        dialogue = Dialogue(dialogue_id=current_dialogue_id, agent_ids=agent_ids,
                            problem=domain_case2send.problem)

        # Store the initial date of dialogue and send it to the commitment store
        self.agent.dialogue_init_time = datetime.now().microsecond
        trigger_msg = create_message(self.agent.commitment_store_id, self.agent.commitment_store_id, self.agent.my_id,
                                     self.agent.my_id, ADD_DIALOGUE_PERF, current_dialogue_id, None)
        await self.send(trigger_msg)
