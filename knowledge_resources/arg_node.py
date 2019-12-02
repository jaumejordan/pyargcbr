from enum import Enum


class NodeType(Enum):
    FIRST = 1
    LAST = 2
    NODE = 3
    AGREE = 4


class ArgNode:
    def __init__(self, arg_case_id: int, child_arg_case_id_list: list, parent_arg_case_id: int, node_type: NodeType):
        self.arg_case_id = arg_case_id
        self.child_arg_case_id_list = child_arg_case_id_list
        self.parent_arg_case_id = parent_arg_case_id
        self.node_type = node_type

    def delete_arg_node(self, arg_case_id: int):
        self.child_arg_case_id_list.remove(arg_case_id)
