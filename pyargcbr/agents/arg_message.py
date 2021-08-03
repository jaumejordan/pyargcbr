from typing import List, Optional, Any, Union

from .protocol import MessageCodification as msg_cod
from loguru import logger
from spade.message import Message

from pyargcbr.agents.protocol import NO_COMMIT_PERF, ASSERT_PERF, ATTACK_PERF, CONVERSATION, PERFORMATIVE, \
    MessageCodification


class ArgMessage(Message):
    to: List[str]

    def __init__(self, agent_ids: List[str] = None):
        super().__init__()
        if not agent_ids:
            self.to = []
        self.to = agent_ids


def create_message(my_id: str, commitment_store_id: str, name: str, recipients: Union[str, List[str]],
                   performative: str, dialogue_id: str, content_object: Optional[Any]) -> ArgMessage:
    """Creates and returns an message with the given arguments.

    Args:
        my_id (str): Sender ID
        commitment_store_id (str): Commitment Store ID
        name (str): Sender name
        recipients (Union[str, List[str]]): The agent(s) ID(s) to send the message to
        performative (str): The performative for the message
        dialogue_id (str): The dialogue ID
        content_object (Any): The object to be attached to the message

    Returns:
        ArgMessage: The message to be sent
    """
    msg = ArgMessage()
    msg.sender = my_id
    if type(recipients) == str:
        msg.to.append(recipients)
    else:
        msg.to = recipients
    if performative == NO_COMMIT_PERF or performative == ASSERT_PERF or performative == ATTACK_PERF:
        msg.to.append(commitment_store_id)
    msg.set_metadata(CONVERSATION, dialogue_id)

    if '=' in performative:
        index = performative.index("=")
        content_agent_id = performative[index + 1:]
        performative = performative[:index]
        msg.set_metadata("agent_id", content_agent_id)
    msg.set_metadata(PERFORMATIVE, performative)

    if content_object:
        msg.body = msg_cod.pickle_object(content_object)

    receivers_str = ""
    for receiver in msg.to:
        receivers_str += receiver[:receiver.index("@")] + " "

    logger.info("{} message to send to: {} | performative: {}", name, receivers_str,
                msg.get_metadata(PERFORMATIVE))
    return msg
