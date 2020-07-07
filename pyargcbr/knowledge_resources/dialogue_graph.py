from dataclasses import dataclass, field
from typing import List, Union

from .arg_node import ArgNode, NodeType


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

    def add_node(self, node: ArgNode):
        """Adds a node to the nodes list

        Args:
            node (ArgNode): The new node for the list
        """
        self.nodes.append(node)

    def distance_to_final(self, arg_node: Union[ArgNode, int]) -> int:
        """Gets the distance to the final node from the provided node. The node can be provided
        via its ID or via the node itself

        Args:
            arg_node (Union[ArgNode, int]): The provided node

        Returns:
            int: The amount of nodes between the provided one and the last one. If
            the provided node is not contained in the graph returns the size of
            the graph

        Raises:
            TypeError: When the type of the parameter is neither an ArgNode nor an int
            ValueError: When the node provided is not a node of the dialogue graph
        """
        arg_pos = -2
        distance = 0
        if type(arg_node) is int:
            arg_pos += 1
            for node in self.nodes:
                arg_pos += 1
                if node.arg_case_id == arg_node:
                    break
        elif type(arg_node) is ArgNode:
            arg_pos += 1
            for node in self.nodes:
                arg_pos += 1
                if node == arg_node:
                    break
        if arg_node < -1:
            raise TypeError
        elif arg_node < 0:
            raise ValueError
        for j in range(arg_pos, self.size()):
            if self.nodes[j].arg_case_id == NodeType.AGREE:
                break
            distance += 1
        return distance
