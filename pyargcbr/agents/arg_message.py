from typing import List

from spade.message import Message


class ArgMessage(Message):
    to: List[str]

    def __init__(self):
        super().__init__()
        self.to = []
