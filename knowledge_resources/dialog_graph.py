from dataclasses import dataclass, field

from knowledge_resources.arg_node import ArgNode


@dataclass
class dialog_graph:
    nodes: list[ArgNode] = field(default=ArgNode())

