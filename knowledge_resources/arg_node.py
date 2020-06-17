from dataclasses import dataclass
from enum import Enum
from typing import List


class NodeType(Enum):
    """Different types of nodes considered

    Author:
        Stella Heras
    """
    FIRST = 1
    LAST = 2
    NODE = 3
    AGREE = 4


@dataclass
class ArgNode:
    """Implementation of the concept ArgNode"""
    arg_case_id: int
    child_arg_case_id_list: List[int]
    parent_arg_case_id: int
    node_type: NodeType

    def delete_child_arg_node(self, arg_case_id: int):
        """Deletes an ArgNode from the list of ArgumentCase Children IDs

        Args:
            arg_case_id (int): the ID that will be deleted
        """
        self.child_arg_case_id_list.remove(arg_case_id)

    def add_child_arg_node(self, arg_case_id: int):
        """Adds an ArgNode from the list of ArgumentCase Children IDs
        (child_arg_case_id_list)

        Args:
            arg_case_id (int): the ID that will be added
        """
        self.child_arg_case_id_list.append(arg_case_id)
