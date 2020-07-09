from dataclasses import dataclass, field
from enum import Enum
from typing import List, Sequence

from .acceptability_status import AcceptabilityStatus
from .premise import Premise
from .solution import Solution
from ..cbrs import lists_operations


class ArgumentType(Enum):
    """Different types of arguments considered"""
    INDUCTIVE = 1
    PRESUMPTIVE = 2
    MIXED = 3


@dataclass
class ArgumentSolution(Solution):
    """Implementation of the concept ArgumentSolution"""
    argument_type: ArgumentType = None
    acceptability_status: AcceptabilityStatus = AcceptabilityStatus.UNDECIDED
    dist_premises: List[Premise] = field(default_factory=lambda: [])
    presumptions: List[Premise] = field(default_factory=lambda: [])
    exceptions: List[Premise] = field(default_factory=lambda: [])

    counter_examples_arg_case_id: List[int] = field(default_factory=lambda: [])
    counter_examples_dom_case_id: List[int] = field(default_factory=lambda: [])

    def remove_counter_example_arg_case_id(self, old_counter_example_arg_case_id: int):
        """Removes a counter example argument case id from the list of counter
        examples argument cases IDs (counter_examples_arg_case_id)

        Args:
            old_counter_example_arg_case_id (int): The ID that will be removed
        """
        self.counter_examples_arg_case_id.remove(old_counter_example_arg_case_id)

    def remove_counter_example_dom_case_id(self, old_counter_example_dom_case_id: int):
        """Removes a counter example domain case id from the list of counter
        examples domain cases IDs (counter_examples_dom_case_id)

        Args:
            old_counter_example_dom_case_id (int):
        """
        self.counter_examples_dom_case_id.remove(old_counter_example_dom_case_id)

    def remove_distinguishing_premise(self, old_distinguishing_premise: Premise):
        """Removes a distinguishing premise from the distinguishing premises
        list (dist_premises)

        Args:
            old_distinguishing_premise (Premise): The premise that will be
                removed
        """
        self.dist_premises.remove(old_distinguishing_premise)

    def remove_exception(self, old_exception: Premise):
        """Removes a exception from the exceptions list (exceptions)

        Args:
            old_exception (Premise): The exception that will be removed
        """
        self.exceptions.remove(old_exception)

    def remove_presumption(self, old_presumption: Premise):
        """Removes a presumption from the presumptions list

        Args:
            old_presumption (Premise): The presumtion that will be removed
        """
        self.presumptions.remove(old_presumption)

    def add_counter_example_arg_case_id(self, new_counter_example_arg_case_id: int):
        """Adds a counter example argument case id from the list of counter
        examples argument cases IDs (counter_examples_arg_case_id)

        Args:
            new_counter_example_arg_case_id (int): The ID that will be added
        """
        self.counter_examples_arg_case_id.append(new_counter_example_arg_case_id)

    def add_counter_example_dom_case_id(self, new_counter_example_dom_case_id: int):
        """Adds a counter example domain case id from the list of counter
        examples domain cases IDs (counter_examples_dom_case_id)

        Args:
            new_counter_example_dom_case_id (int): The ID that will be added
        """
        self.counter_examples_dom_case_id.append(new_counter_example_dom_case_id)

    def add_distinguishing_premise(self, new_distinguishing_premise: Premise):
        """Adds a distinguishing premise to the distinguishing premises list
        (dist_premises)

        Args:
            new_distinguishing_premise (Premise): The premise that will be added
        """
        self.dist_premises.append(new_distinguishing_premise)

    def add_exception(self, new_exception: Premise):
        """Adds an exception to the exceptions list (exceptions)

        Args:
            new_exception (Premise): The exception that will be added
        """
        self.exceptions.append(new_exception)

    def add_presumption(self, new_presumption: Premise):
        """Adds a presumption to the presumptions list (presumptions)

        Args:
            new_presumption (Premise): The presumption that will be added
        """
        self.presumptions.append(new_presumption)

    def merge_distinguishing_premises(self, new_distinguishing_premises: Sequence[Premise]):
        """Adds new distinguishing premises to the solution skipping the
        duplicates (same ID and content)

        Args:
            new_distinguishing_premises (Sequence[Premise]): New premises to be
                merged with
        """
        Premise.merge_premises_lists(self.dist_premises, new_distinguishing_premises)

    def merge_presumptions(self, new_presumptions: Sequence[Premise]):
        """Adds new presumptions to the solution skipping the duplicates (same
        ID and content)

        Args:
            new_presumptions (Sequence[Premise]): New presumptions to be merged
                with
        """
        Premise.merge_premises_lists(self.dist_premises, new_presumptions)

    def merge_exceptions(self, new_exceptions: Sequence[Premise]):
        """Adds new exceptions to the solution skipping the duplicates (same ID
        and content)

        Args:
            new_exceptions (Sequence[Premise]): New exceptions to be merged with
        """
        Premise.merge_premises_lists(self.dist_premises, new_exceptions)

    def merge_counter_examples_arg_cases_ids(self, new_ids: Sequence[int]):
        """Adds new counter examples IDs to the Solution skipping the duplicates

        Args:
            new_ids: The new IDs to be merged with
        """
        lists_operations.merge_lists_using_sets(self.counter_examples_arg_case_id, new_ids)
        # lists_operations.merge_lists_using_sets(self.counter_examples_arg_case_id, new_ids)

    def merge_counter_examples_dom_cases_ids(self, new_ids: Sequence[int]):
        """Adds new counter examples IDs to the Solution skipping the duplicates

        Args:
            new_ids: The new IDs to be merged with
        """
        lists_operations.merge_lists_using_sets(self.counter_examples_dom_case_id, new_ids)
        # lists_operations.merge_lists_by_looping(self.counter_examples_dom_case_id, new_ids)
