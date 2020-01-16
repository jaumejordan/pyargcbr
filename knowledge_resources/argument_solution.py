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
    dist_premises: list = field(default=[])
    presumptions: list = field(default=[])
    exceptions: list = field(default=[])

    counter_examples_arg_case_id: list = field(default=[])
    counter_examples_dom_case_id: list = field(default=[])

    def remove_counter_example_arg_case_id(self, old_counter_example_arg_case_id: int):
        self.counter_examples_arg_case_id.remove(old_counter_example_arg_case_id)

    def remove_counter_example_dom_case_id(self, old_counter_example_dom_case_id: int):
        self.counter_examples_dom_case_id.remove(old_counter_example_dom_case_id)

    def remove_distinguishing_premise(self, old_distinguishing_premise: Premise):
        self.dist_premises.remove(old_distinguishing_premise)

    def remove_exception(self, old_exception: Premise):
        self.exceptions.remove(old_exception)

    def remove_presumption(self, old_presumption: Premise):
        self.presumptions.remove(old_presumption)

    def add_counter_example_arg_case_id(self, new_counter_example_arg_case_id: int):
        self.counter_examples_arg_case_id.append(new_counter_example_arg_case_id)

    def add_counter_example_dom_case_id(self, new_counter_example_dom_case_id: int):
        self.counter_examples_dom_case_id.append(new_counter_example_dom_case_id)

    def add_distinguishing_premise(self, new_distinguishing_premise: Premise):
        self.dist_premises.append(new_distinguishing_premise)

    def add_exception(self, new_exception: Premise):
        self.exceptions.append(new_exception)

    def add_presumption(self, new_presumption: Premise):
        self.presumptions.append(new_presumption)
