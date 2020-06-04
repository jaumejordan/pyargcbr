import datetime
import asyncio
from asyncio import CancelledError
from typing import Dict, List

from spade.template import Template

from agents.protocol import ADD_ARGUMENT_PERF, REMOVE_ARGUMENT_PERF, ADD_POSITION_PERF, ATTACK_PERF, ADD_POSITION_PERF,\
    GET_POSITION_PERF, GET_ALL_POSITIONS_PERF, NO_COMMIT_PERF, ASSERT_PERF, ATTACK_PERF, ADD_DIALOGUE_PERF,\
    GET_DIALOGUE_PERF, ENTER_DIALOGUE_PERF, WITHDRAW_DIALOGUE_PERF, DIE_PERF, REGISTER_PROTOCOL, REQUEST_PROTOCOL,\
    ACCEPT_PERF, REQUEST_PERF, LAST_MODIFICATION_DATE_PERF, PROTOCOL, PERFORMATIVE, CONVERSATION

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message

from knowledge_resources.argument import Argument
from knowledge_resources.dialogue import Dialogue
from knowledge_resources.position import Position


class CommitmentStore(Agent):
    """This agent, named Commitment Store, stores all the information about the dialogues, including: positions,
    arguments and modification times.
    It responds to the petitions of the agents in the dialogue process"""
    def __init__(self, agentjid, password):
        super().__init__(jid=agentjid, password=password)
        self.agent_id = agentjid
        self.dialogues: Dict[str, Dialogue] = {}
        self.arguments: Dict[str, Dict[str, List[Argument]]] = {}
        self.positions: Dict[str, Dict[str, Position]] = {}
        self.last_modifications: Dict[str, int] = {}

    def finalize(self):
        pass

    async def setup(self):
        print("Commitment Store starting . . .")

        try:
            template = Template()
            template.set_metadata(PROTOCOL, REGISTER_PROTOCOL)
            register_behaviour = RegistrationBehaviour()
            self.add_behaviour(register_behaviour, template)
            while not self.has_behaviour(register_behaviour):
                print("Commitment Store {} could not create RegisterBehaviour. Retrying...".format(self.agent_id))
                self.add_behaviour(register_behaviour, template)
        except Exception as e:
            print("EXCEPTION creating RegisterBehaviour in Directory {}: {}".format(self.agent_id, e))

        try:
            template = Template()
            template.set_metadata(PROTOCOL, REQUEST_PROTOCOL)
            replier_behaviour = ReplierBehaviour()
            self.add_behaviour(replier_behaviour, template)
            while not self.has_behaviour(replier_behaviour):
                print("Commitment Store {} could not create ReplierBehaviour. Retrying...".format(self.agent_id))
                self.add_behaviour(replier_behaviour, template)
        except Exception as e:
            print("EXCEPTION creating ReplierBehaviour in Directory {}: {}".format(self.agent_id, e))

    def create_message(self, agent_jid: str, performative: str, conversation_id: str, content_object) -> Message:
        msg = Message()
        msg.to = agent_jid
        msg.set_metadata(CONVERSATION, conversation_id) # TODO check
        msg.set_metadata(PERFORMATIVE, performative)
        msg.body = content_object
        print(self.name, ": message to send to: ", msg.to, " dialogueID: ", msg.get_metadata(CONVERSATION))
        return msg

    def add_argument(self, arg: Argument, agent_id: str, dialogue_id: str) -> None:
        """Adds an argument to the corresponding list of the dialogue and the agent

        Args:
            arg (Argument): The argument to store
            agent_id (str): The id of the agent that uses the argument
            dialogue_id (str): Dialogue identifier where the argument is used
        """
        agent_arg = self.arguments.get(agent_id, {})
        arg_list = agent_arg.get(dialogue_id, [])
        arg_list.append(arg)
        agent_arg[dialogue_id] = arg_list
        self.arguments[agent_id] = agent_arg

    def get_arguments(self, agent_id: str, dialogue_id: str) -> List[Argument]:
        """Returns the arguments that has used an agent in a dialogue

        Args:
            agent_id (str): Agent identifier
            dialogue_id (str): Dialogue identifier

        Returns:
            List[Argument]: Arguments that has used an agent in a dialogue
        """
        return self.arguments.get(agent_id, {}).get(dialogue_id, [])

    def remove_argument(self, old_arg: Argument, agent_id: str, dialogue_id: str) -> None:
        """Remove an argument that has used an agent in a dialogue

        Args:
            old_arg (Argument): Argument to remove
            agent_id (str): Agent identifier
            dialogue_id (str): Dialogue identifier
        """
        arguments_list = [arg for arg in self.get_arguments(agent_id, dialogue_id) if arg.id != old_arg.id]
        if not self.arguments[agent_id]:
            self.arguments[agent_id] = {}
        self.arguments[agent_id][dialogue_id] = arguments_list

    def add_position(self, pos: Position, agent_id: str, dialogue_id: str) -> None:
        """Sets the position to the corresponding agent in the given dialogue

        Args:
            pos (Argument): The position to store
            agent_id (str): The id of the agent that has the position
            dialogue_id (str): Dialogue identifier corresponding to the position
        """
        agent_pos = self.positions.get(agent_id, {})
        agent_pos[dialogue_id] = pos
        self.positions[agent_id] = agent_pos

    def get_positions(self, agent_id: str, dialogue_id: str) -> Position:
        """Returns the position of the given agent in the given dialogue

        Args:
            agent_id (str): Agent identifier
            dialogue_id (str): Dialogue identifier

        Returns:
            Position: The position to the corresponding agent in the given dialogue
        """
        return self.positions.get(agent_id, {}).get(dialogue_id, [])

    def get_all_positions(self, dialogue_id: str, my_agent_id: str = "") -> List[Position]:
        """Returns all the positions of the dialogue
        (it does not include the position of the agent specified in the second parameter, normally the requester)

        Args:
            dialogue_id (str): Dialogue identifier
            my_agent_id (str): Agent identifier. Default is ""

        Returns:
            All the positions of the given dialogue (except for the ones corresponding to thepassed agent)
        """
        positions_list: List[Position] = []
        dialogue = self.dialogues.get(dialogue_id)
        agent_ids = dialogue.agent_ids
        for agent_id in agent_ids:
            if agent_id == my_agent_id:  # Not include the position of the agent that requests
                continue
            agent_positions = self.positions.get(agent_id)
            if agent_positions:
                pos = agent_positions.get(dialogue_id)
                if pos:
                    positions_list.append(pos)
        return positions_list

    def remove_position(self, old_pos: Position, agent_id: str, dialogue_id: str) -> None:
        """Removes the position of the given agent in the given dialogue

        Args:
            old_pos (Argument): Position to remove
            agent_id (str): Agent identifier
            dialogue_id (str): Dialogue identifier
        """
        self.positions[agent_id].pop(dialogue_id)

    def add_dialogue(self, dialogue: Dialogue) -> None:
        """Adds a dialogue to the dialogues

        Args:
            dialogue: Dialogue to store
        """
        self.dialogues[dialogue.dialogue_id] = dialogue

    def get_dialogue(self, dialogue_id: str) -> Dialogue:
        """Returns the Dialogue specified by the identifier

        Args:
            dialogue_id: Dialogue identifier
        """
        return self.dialogues.get(dialogue_id)


class RegistrationBehaviour(CyclicBehaviour):
    async def on_start(self):
        print("Starting RegistrationBehaviour")

    async def send_confirmation(self, agent_id):
        """
        Send a ``spade.message.Message`` with an acceptance to manager/station to register in the dictionary
        """
        reply = Message()
        reply.to = str(agent_id)
        reply.set_metadata(PROTOCOL, REGISTER_PROTOCOL)
        reply.set_metadata(PERFORMATIVE, ACCEPT_PERF)
        await self.send(reply)

    async def run(self):
        try:
            msg = await self.receive(timeout=5)
            if msg:
                agent_id = msg.sender
                performative = msg.get_metadata(PERFORMATIVE)
                if performative == REQUEST_PERF:
                    print("Registration in the Commitment Store {} of the agent {}".format(self.agent.name,
                                                                                           agent_id))
                    await self.send_confirmation(agent_id)
        except CancelledError:
            print("Cancelling async tasks...")
        except Exception as e:
            print("EXCEPTION in DirectoryRegister Behaviour of Commitment Store {}: {}".format(self.agent.name, e))


class ReplierBehaviour(CyclicBehaviour):
    def __init__(self):
        super().__init__()
        self.last_modification_date = "19/2/2013"

    async def on_start(self):
        print("Starting behaviour . . .")

    async def run(self):
        try:
            print("WAITING")
            msg = await self.receive(timeout=5)
            if msg:
                agent_id = msg.sender
                performative = msg.get_metadata(PERFORMATIVE)
                print(msg)
                if performative == LAST_MODIFICATION_DATE_PERF:
                    pass
                elif performative == ADD_ARGUMENT_PERF:
                    pass
                elif performative == REMOVE_ARGUMENT_PERF:
                    pass
                elif performative == ADD_POSITION_PERF:
                    pass
                elif performative == GET_POSITION_PERF:
                    pass
                elif performative == GET_ALL_POSITIONS_PERF:
                    pass
                elif performative == NO_COMMIT_PERF:
                    pass
                elif performative == ADD_DIALOGUE_PERF:
                    pass
                elif performative == GET_DIALOGUE_PERF:
                    pass
                elif performative == ENTER_DIALOGUE_PERF:
                    pass
                elif performative == WITHDRAW_DIALOGUE_PERF:
                    pass
                elif performative == DIE_PERF:
                    pass
                else:
                    print("{} not understood".format(self.agent))
        except CancelledError:
            pass
        except Exception as e:
            pass
