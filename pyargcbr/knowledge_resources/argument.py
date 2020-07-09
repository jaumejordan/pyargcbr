from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .acceptability_status import AcceptabilityStatus
from .conclusion import Conclusion
from .social_context import DependencyRelation
from .support_set import SupportSet


@dataclass
class Argument:
    """Implementation of the concept Argument"""
    id: int = 1
    conclusion: Conclusion = Conclusion()
    times_used_conclusion: int = 0
    value: str = ""
    support_set: SupportSet = SupportSet()
    proponent_depen_relation: Optional[DependencyRelation] = None
    acceptability_state: AcceptabilityStatus = AcceptabilityStatus.UNDECIDED
    attacking_to_arg_id: int = -1
    received_attacks_counter_examples: List[Argument] = field(default_factory=lambda: [])
    received_attacks_dist_premises: List = field(default_factory=lambda: [])

    def __str__(self):
        """Default 'to string' method rewritten

        Returns:
            A descriptive str of the Argument
        """
        return "id=" + str(self.id) + "sol_id= " + str(self.conclusion.id) + str(self.conclusion.id) + \
               " promoted_value=" + self.value + " attacking_to_arg_id=" + str(self.attacking_to_arg_id) + \
               "\nSupport Set: " + str(self.support_set)

    def add_received_attacks_counter_examples(self, new_arg: Argument):
        """Adds an argument to the list of received attacks counter examples
        (received_attacks_counter_examples)

        Args:
            new_arg (Argument): The new argument that will be added
        """
        self.received_attacks_counter_examples.append(new_arg)

    def add_received_attacks_dist_premises(self, old_arg: Argument):
        """Removes an argument of the list of received attacks counter examples
        (received_attacks_counter_examples)

        Args:
            old_arg (Argument): The new argument that will be added
        """
        self.received_attacks_dist_premises.append(old_arg)
