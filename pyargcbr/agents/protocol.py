import codecs
import pickle
from typing import TypeVar, Any

from spade.message import Message

PROTOCOL = "protocol"
PERFORMATIVE = "performative"

REGISTER_PROTOCOL = "REGISTER"
REQUEST_PROTOCOL = "REQUEST"

REQUEST_PERF = "request"  # To ask for registration
ACCEPT_PERF = "accept"  # To confirm registration

LAST_MODIFICATION_DATE_PERF = "last_modification_date"
ADD_ARGUMENT_PERF = "add_argument"
REMOVE_ARGUMENT_PERF = "remove_argument"
ADD_POSITION_PERF = "add_position"
GET_POSITION_PERF = "get_position"
GET_ALL_POSITIONS_PERF = "get_all_positions"
NO_COMMIT_PERF = "no_commit"
ASSERT_PERF = "assert"
ATTACK_PERF = "attack"
ADD_DIALOGUE_PERF = "add_dialogue"
GET_DIALOGUE_PERF = "get_dialogue"
ENTER_DIALOGUE_PERF = "enter_dialogue"
WITHDRAW_DIALOGUE_PERF = "withdraw_dialogue"
DIE_PERF = "die"
OPEN_DIALOGUE_PERF = "open_dialogue"

WHY_PERF = "why"
NOTHING_PERF = "nothing"
FINISH_DIALOGUE_PERF = "finish_dialogue"
ACCEPTS_PERF = "accepts"
ATTACKS_PERF = "attack"
ASSERTS_PERF = "asserts"

CONVERSATION = "conversation"

MSG_TIMEOUT = 5


class MessageCodification:
    PickledObject = TypeVar("PickledObject")

    @staticmethod
    def pickle_object(obj: Any) -> PickledObject:
        return codecs.encode(pickle.dumps(obj), "base64").decode()

    @staticmethod
    def unpickle_object(obj: PickledObject):
        return pickle.loads(codecs.decode(obj.encode(), "base64"))

    @staticmethod
    def get_decoded_message_content(msg: Message) -> Any:
        return MessageCodification.unpickle_object(msg.body)
