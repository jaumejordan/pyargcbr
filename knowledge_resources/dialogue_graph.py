from dataclasses import dataclass, field
from typing import List

from knowledge_resources.arg_node import ArgNode, NodeType


@dataclass
class DialogueGraph:
    nodes: List[ArgNode] = field(default=[])

    def remove_node(self, old_node: ArgNode):
        self.nodes.remove(old_node)

    def get_root(self):
        for node in self.nodes:
            if node.node_type == NodeType.FIRST:
                return node
        return None

    def size(self):
        return len(self.nodes)

    def __contains__(self, arg_id: int):
        for node in self.nodes:
            if node.arg_case_id == arg_id:
                return True
        return False

    def get_node(self, arg_id: int):
        for node in self.nodes:
            if node.arg_case_id == arg_id:
                return node
        return None

    def get_nodes(self, arg_id: int):
        arg_n = []
        for node in self.nodes:
            if node.arg_case_id == arg_id:
                arg_n.append(node)
        return arg_n

    def distance_to_final(self, arg_node):
        arg_pos = 1
        distance = 0
        if type(arg_node) is int:
            for node in self.nodes:
                if node.arg_case_id == arg_node:
                    break
                arg_pos += 1
        elif type(arg_node) is ArgNode:
            for node in self.nodes:
                if node == arg_node:
                    break
                arg_pos += 1
        for j in range(arg_pos, self.size()):
            if self.nodes[j].arg_case_id == NodeType.AGREE:
                break
            distance += 1
        return distance

    # TODO:  Revisar método distance_to_final, en java estaba implementado como dos métodos sobrecargados, esto es replicable en python usando @typing.overload
    """
    def distance_to_final(self, arg_id: int):
        arg_pos = 1
        distance = 0
        for node in self.nodes:
            if node.get_id() == arg_id:
                break
            arg_pos += 1
        for j in range(arg_pos, self.size()):
            if self.nodes[j].get_node_type() == NodeType.AGREE:
                break
            distance += 1
        return distance

    def distance_to_final(self, arg_node: ArgNode):
        arg_pos = 1
        distance = 0
        for node in self.nodes:
            if node == arg_node:
                break
            arg_pos += 1
        for j in range(arg_pos, self.size()):
            if self.nodes[j].get_node_type() == NodeType.AGREE:
                break
            distance += 1
        return distance
    """
