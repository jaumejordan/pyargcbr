from dataclasses import dataclass
from enum import Enum


class NodeType(Enum):
    FIRST = 1
    LAST = 2
    NODE = 3
    AGREE = 4


@dataclass
class ArgNode:
    arg_case_id: int
    child_arg_case_id_list: list
    parent_arg_case_id: int
    node_type: NodeType

    def delete_arg_node(self, arg_case_id: int):
        self.child_arg_case_id_list.remove(arg_case_id)

    def add_arg_node(self, arg_case_id: int):
        self.child_arg_case_id_list.append(arg_case_id)
