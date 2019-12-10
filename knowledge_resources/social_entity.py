from dataclasses import dataclass, field
from knowledge_resources import valpref


@dataclass
class SocialEntity:
    ValPref: valpref
    id: int = 1
    name: str = ""
    role: str = ""
    norms: list[str] = field(default=[])
