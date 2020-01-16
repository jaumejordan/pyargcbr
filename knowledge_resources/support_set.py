from dataclasses import dataclass, field

from knowledge_resources.argument_case import ArgumentCase
from knowledge_resources.argumentation_scheme import ArgumentationScheme
from knowledge_resources.domain_case import DomainCase
from knowledge_resources.premise import Premise


@dataclass
class SupportSet:
    premises: list = field(default=[])
    domain_cases: list = field(default=[])
    argument_cases: list = field(default=[])
    schemes: list = field(default=[])
    dist_premises: list = field(default=[])
    presumptions: list = field(default=[])
    exceptions: list = field(default=[])

    counter_examples_dom_cases: list = field(default=[])
    counter_examples_arg_cases: list = field(default=[])

    def remove_argumentation_scheme(self, old_argumentation_scheme: ArgumentationScheme):
        self.schemes.remove(old_argumentation_scheme)

    def add_argumentation_case(self, new_argumentation_scheme: ArgumentationScheme):
        self.schemes.append(new_argumentation_scheme)

    def add_counter_example_arg_case_id(self, new_argument_case: ArgumentCase):
        self.counter_examples_arg_cases.append(new_argument_case)

    def add_counter_example_dom_case_id(self, new_argument_case: ArgumentCase):
        self.counter_examples_dom_cases.append(new_argument_case)

    def remove_counter_example_arg_case_id(self, old_argument_case: ArgumentCase):
        self.counter_examples_arg_cases.remove(old_argument_case)

    def remove_counter_example_dom_case_id(self, old_argument_case: ArgumentCase):
        self.counter_examples_dom_cases.remove(old_argument_case)

    def add_argument_case(self, new_argument_case: ArgumentCase):
        self.argument_cases.append(new_argument_case)

    def remove_argument_case(self, old_argument_case: ArgumentCase):
        self.argument_cases.remove(old_argument_case)

    def add_distinguising_premise(self, new_distinguising_premise: Premise):
        self.dist_premises.append(new_distinguising_premise)

    def remove_distinguising_premise(self, old_distinguising_premise: Premise):
        self.dist_premises.remove(old_distinguising_premise)

    def add_domain_case(self, new_domain_case: DomainCase):
        self.dist_premises.append(new_domain_case)

    def remove_domain_case(self, old_domain_case: Premise):
        self.dist_premises.remove(old_domain_case)

    def add_premise(self, new_premise: Premise):
        self.premises.append(new_premise)

    def remove_premise(self, old_premise: Premise):
        self.premises.remove(old_premise)

    def add_presumption(self, new_presumption: Premise):
        self.presumptions.append(new_presumption)

    def remove_presumption(self, old_presumption: Premise):
        self.presumptions.remove(old_presumption)

    def __str__(self):
        st = ""
        if self.premises and len(self.premises) > 0:
            st += "premises: "
            for p in self.premises:
                st += str(p.id) + "=" + p.contennt + " "

        if self.dist_premises and len(self.dist_premises) > 0:
            st += "\ndist_premises: "
            for p in self.dist_premises:
                st += str(p.id) + "=" + p.contennt + " "

        if self.counter_examples_arg_cases and len(self.counter_examples_arg_cases) > 0:
            st += "\ndist_premises: "
            for arg_case in self.counter_examples_arg_cases:
                st += "arc_case_id=" + str(arg_case.id) + " "

        return st

