from dataclasses import dataclass, field
from enum import Enum

from knowledge_resources.acceptability_status import AcceptabilityStatus
from knowledge_resources.premise import Premise
from knowledge_resources.solution import Solution


class ArgumentType(Enum):
    INDUCTIVE = 1
    PRESUMPTIVE = 2
    MIXED = 3

@dataclass
class ArgumentSolution(Solution):
    argument_type: ArgumentType = None
    acceptability_status: AcceptabilityStatus = AcceptabilityStatus.UNDECIDED
    dist_premises: list[Premise] = field(default=[])
    presumptions: list[Premise] = field(default=[])
    exceptions: list[Premise] = field(default=[])

    counter_examples_arg_case_id: list(int) = field(default=[])
    counter_examples_dom_case_id: list(int) = field(default=[])

    def remove_counter_example_arg_case_id(self, old_counter_example_arg_case_id: int):
        self.counter_examples_arg_case_id.remove(old_counter_example_arg_case_id)

    def remove_(self, old_counter_example_dom_case_id: int):
        self.counter_examples_dom_case_id.remove(old_counter_example_dom_case_id)

    def remove_(self, old_distinguishing_premise: Premise):
        self.dist_premises.remove(old_distinguishing_premise)

    def remove_(self, old_exception: Premise):
        self.exceptions.remove(old_exception)

    def remove_(self, old_presumption: Premise):
        self.presumptions.remove(old_presumption)


