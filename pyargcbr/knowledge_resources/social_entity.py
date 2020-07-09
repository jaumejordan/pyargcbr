from dataclasses import dataclass, field
from typing import List

from .norm import Norm
from .valpref import ValPref


@dataclass
class SocialEntity:
    """Implementation of the concept SocialEntity"""
    id: int = 1
    name: str = ""
    role: str = ""
    norms: List[Norm] = field(default_factory=lambda: [])
    valpref: ValPref = ValPref()

    def remove_norm(self, old_norm: Norm):
        """Removes a norm from the norms list (norms)
        Args:
            old_norm (Norm): The norm that will be removed
        """
        self.norms.remove(old_norm)

    def add_norm(self, new_norm: Norm):
        """Adds a norm to the norms list (norms)
        Args:
            new_norm (Norm): The norm that will be added
        """
        self.norms.append(new_norm)
