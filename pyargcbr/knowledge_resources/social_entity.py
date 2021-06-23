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

    def __ne__(self, o) -> bool:
        """Returns True if the SocialEntity being compared is equal. Otherwise, return False
        Args:
            o (SocialEntity): The other SocialEntity
        """
        if self.id != o.id:
            return True
        elif self.name != o.name:
            return True
        elif self.role != o.role:
            return True
        elif self.norms != o.norms:
            return True
        elif self.valpref != o.valpref:
            return True
        else:
            return False

    def __eq__(self, other):
        """Returns True if the SocialEntity being compared is different. Otherwise, return False
        Args:
            o (SocialEntity): The other SocialEntity
        """
        return not self.__ne__(other)


