from dataclasses import dataclass, field
from typing import List

from .argument_case import ArgumentCase
from .argumentation_scheme import ArgumentationScheme
from .domain_case import DomainCase
from .premise import Premise


@dataclass
class SupportSet:
    """Implementation of the concept SupportSet"""
    premises: List[Premise] = field(default_factory=lambda: [])
    domain_cases: List[DomainCase] = field(default_factory=lambda: [])
    argument_cases: List[ArgumentCase] = field(default_factory=lambda: [])
    schemes: List[ArgumentationScheme] = field(default_factory=lambda: [])
    dist_premises: List[Premise] = field(default_factory=lambda: [])
    presumptions: List[Premise] = field(default_factory=lambda: [])
    exceptions: List[Premise] = field(default_factory=lambda: [])

    counter_examples_dom_cases: List[DomainCase] = field(default_factory=lambda: [])
    counter_examples_arg_cases: List[ArgumentCase] = field(default_factory=lambda: [])

    def remove_argumentation_scheme(self, old_argumentation_scheme: ArgumentationScheme):
        """Removes an argumentation scheme from the list of argumentation
        schemes (schemes)

        Args:
            old_argumentation_scheme (ArgumentationScheme): The scheme that will
                be removed
        """
        self.schemes.remove(old_argumentation_scheme)

    def add_argumentation_case(self, new_argumentation_scheme: ArgumentationScheme):
        """Adds an argumentation scheme to the list of argumentation schemes
        (schemes)

        Args:
            new_argumentation_scheme (ArgumentationScheme): The scheme that will
                be added
        """
        self.schemes.append(new_argumentation_scheme)

    def add_counter_example_arg_case_id(self, new_argument_case: ArgumentCase):
        """Adds a counter example argument case ID to the list of counter
        example argument cases IDs list (counter_examples_arg_cases)

        Args:
            new_argument_case (ArgumentCase): The ID that will be added
        """
        self.counter_examples_arg_cases.append(new_argument_case)

    def add_counter_example_dom_case_id(self, new_domain_case: DomainCase):
        """Adds a counter example domain case ID to the list of counter example
        domain cases IDs list (counter_examples_dom_cases)

        Args:
            new_domain_case (DomainCase): The ID that will be added
        """
        self.counter_examples_dom_cases.append(new_domain_case)

    def remove_counter_example_arg_case_id(self, old_argument_case: ArgumentCase):
        """Removes a counter example argument case ID from the list of counter
        example argument cases IDs list (counter_examples_arg_cases)

        Args:
            old_argument_case (ArgumentCase): The ID that will be removed
        """
        self.counter_examples_arg_cases.remove(old_argument_case)

    def remove_counter_example_dom_case_id(self, old_adomain_case: DomainCase):
        """Removes a counter example domain case ID from the list of counter
        example domain cases IDs list (counter_examples_dom_cases)

        Args:
            old_adomain_case (DomainCase): The ID that will be removed
        """
        self.counter_examples_dom_cases.remove(old_adomain_case)

    def add_argument_case(self, new_argument_case: ArgumentCase):
        """Adds an argument case to the argument cases list (argument_cases)

        Args:
            new_argument_case (ArgumentCase): The case that will be added
        """
        self.argument_cases.append(new_argument_case)

    def remove_argument_case(self, old_argument_case: ArgumentCase):
        """Removes an argument case from the argument cases list
        (argument_cases)

        Args:
            old_argument_case (ArgumentCase): The case that will be removed
        """
        self.argument_cases.remove(old_argument_case)

    def add_distinguishing_premise(self, new_distinguishing_premise: Premise):
        """Adds a distinguishing premise to the distinguishing premises list
        (dist_premises)

        Args:
            new_distinguishing_premise (Premise): The premise that will be added
        """
        self.dist_premises.append(new_distinguishing_premise)

    def remove_distinguishing_premise(self, old_distinguishing_premise: Premise):
        """Removes a distinguishing premise from the distinguishing premises
        list (dist_premises)

        Args:
            old_distinguishing_premise (Premise): The premise that will be
                removed
        """
        self.dist_premises.remove(old_distinguishing_premise)

    def add_domain_case(self, new_domain_case: DomainCase):
        """Adds a domain case to the domain cases list (domain_cases)

        Args:
            new_domain_case (DomainCase): The domain case that will be added
        """
        self.domain_cases.append(new_domain_case)

    def remove_domain_case(self, old_domain_case: Premise):
        """Removes a domain case from the domain cases list (domain_cases)

        Args:
            old_domain_case (Premise): The domain case that will be removed
        """
        self.domain_cases.remove(old_domain_case)

    def add_premise(self, new_premise: Premise):
        """Adds a premise to the premises list (premises)

        Args:
            new_premise (Premise): The premise that will be added
        """
        self.premises.append(new_premise)

    def remove_premise(self, old_premise: Premise):
        """Removes a premise from the premises list (premises)

        Args:
            old_premise (Premise): The premise that will be removed
        """
        self.premises.remove(old_premise)

    def add_presumption(self, new_presumption: Premise):
        """Adds a presumption to the presumptions list (presumptions)

        Args:
            new_presumption (Premise): The presumption that will be added
        """
        self.presumptions.append(new_presumption)

    def remove_presumption(self, old_presumption: Premise):
        """Removes a presumption from the presumptions list (presumptions)

        Args:
            old_presumption (Premise): The presumption that will be removed
        """
        self.presumptions.remove(old_presumption)

    def __str__(self) -> str:
        """Default 'to string' method rewritten

        Returns:
            str: A descriptive str of the SupportSet
        """
        st = ""
        if self.premises and len(self.premises) > 0:
            st += "premises: "
            for p in self.premises:
                st += str(p.id) + "=" + p.content + " "

        if self.dist_premises and len(self.dist_premises) > 0:
            st += "\ndist_premises: "
            for p in self.dist_premises:
                st += str(p.id) + "=" + p.content + " "

        if self.counter_examples_arg_cases and len(self.counter_examples_arg_cases) > 0:
            st += "\ndist_premises: "
            for arg_case in self.counter_examples_arg_cases:
                st += "arc_case_id=" + str(arg_case.id) + " "

        return st
