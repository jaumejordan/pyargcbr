from dataclasses import dataclass, field
from typing import Dict, Sequence

from .premise import Premise


@dataclass
class DomainContext:
    """Implementation of the concept DomainCase"""
    premises: Dict[int, Premise] = field(default_factory=lambda: {})

    def remove_premise(self, old_premise: Premise):
        """Removes a premise from the premises dict

        Args:
            old_premise (Premise): The premise that will be removed
        """
        del self.premises[old_premise.id]

    def add_premise(self, new_premise: Premise):
        """Adds a premise to the premises dict

        Args:
            new_premise (Premise): The premise that will be added
        """
        self.premises[new_premise.id] = new_premise

    def set_premises_from_list(self, new_premises: Sequence[Premise]):
        """Sets the premises dict (premises) values from the provided list. If a
        premise from the dict shares ID with one of the list it's overwritten

        Args:
            new_premises (Sequence[Premise]): The list of new premises
        """
        for new_premise in new_premises:
            self.premises[new_premise.id] = new_premise
