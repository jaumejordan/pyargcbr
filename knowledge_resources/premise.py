from dataclasses import dataclass, field


@dataclass
class Premise:
    id: int = -1
    name: str = field(default="", compare=False)
    content: str = field(default="", compare=False)
