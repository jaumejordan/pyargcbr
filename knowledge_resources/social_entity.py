from dataclasses import dataclass, field
from knowledge_resources.norm import Norm
from knowledge_resources.valpref import ValPref


@dataclass
class SocialEntity:
    id: int = 1
    name: str = ""
    role: str = ""
    norms: list[Norm] = field(default=[])
    valpref: ValPref = ValPref()

    def delete_norm(self, old_norm: Norm):
        self.norms.remove(old_norm)

    def add_norm(self, new_norm: Norm):
        self.norms.append(new_norm)
