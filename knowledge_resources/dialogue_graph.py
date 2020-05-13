from dataclasses import dataclass, field
from typing import List, Union

from knowledge_resources.arg_node import ArgNode, NodeType


@dataclass
class DialogueGraph:
    """Implementation of the concept DialogueGraph

    Each argument given by an agent, and received, will be stored as an
    argument node in a list of dialogue graphs of the current dialogue (take
    into account that a dialogue includes a lot of subdialogues between two
    agents, this is why we store a list of dialogue graphs). Then, when the
    agent stores all the arguments of the whole dialogue, will use the dialogue
    graphs to introduce it in every corresponding argument case
    """
    nodes: List[ArgNode] = field(default_factory=lambda: [])

    def remove_node(self, old_node: ArgNode):
        """Removes an argument node from the argument nodes list (nodes)

        Args:
            old_node (ArgNode): The node that will be removed
        """
        self.nodes.remove(old_node)

    def get_root(self) -> Union[ArgNode, None]:
        """Gets the root argument node of the dialogue graph

        Returns:
            ArgNode, None: The root node
        """
        for node in self.nodes:
            if node.node_type == NodeType.FIRST:
                return node
        return None

    def size(self) -> int:
        """Gets the size of the dialogue graph

        Returns:
            int: The number of nodes contained in the graph
        """
        return len(self.nodes)

    def __contains__(self, arg_id: int) -> bool:
        """Checks whether a node exists in the graph or not

        Args:
            arg_id (int): The node that will be searched

        Returns:
            bool: True if the graph contains the node, False otherwise
        """
        for node in self.nodes:
            if node.arg_case_id == arg_id:
                return True
        return False

    def get_node(self, arg_id: int) -> Union[ArgNode, None]:
        """Gets a node from the graph with the provided ID (if exists)

        Args:
            arg_id (int): The ID of the node that will be searched

        Returns:
            ArgNode, None: The argument node if it is contained, None otherwise
        """
        for node in self.nodes:
            if node.arg_case_id == arg_id:
                return node
        return None

    def get_nodes(self, arg_id: int) -> List[ArgNode]:
        """Gets all the nodes of the graph that share the same provided ID

        Args:
            arg_id (int): The provided ID

        Returns:
            List[ArgNode]: A list of argument nodes with the ID provided
        """
        arg_n = []
        for node in self.nodes:
            if node.arg_case_id == arg_id:
                arg_n.append(node)
        return arg_n

    def distance_to_final(self, arg_node: ArgNode) -> int:
        """Gets the distance to the final node from the provided node

        Args:
            arg_node (ArgNode): The provided node

        Returns:
            int: The amount of nodes between the provided one and the last one. If
            the provided node is not contained in the graph returns the size of
            the graph
        """
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
