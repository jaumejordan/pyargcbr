from dataclasses import dataclass, field
from typing import List, Sequence

from .argumentation_scheme import ArgumentationScheme
from .dialogue_graph import DialogueGraph
from .justification import Justification
from ..cbrs import lists_operations


@dataclass
class ArgumentJustification(Justification):
    """Implementation of the concept ArgumentJustification"""
    domain_cases_ids: List[int] = field(default_factory=lambda: [])
    argument_cases_ids: List[int] = field(default_factory=lambda: [])
    schemes: List[ArgumentationScheme] = field(default_factory=lambda: [])
    dialogue_graphs: List[DialogueGraph] = field(default_factory=lambda: [])

    def remove_argumentation_scheme(self, old_argumentation_scheme: ArgumentationScheme):
        """Removes an argumentation scheme from the schemes list (schemes)

        Args:
            old_argumentation_scheme (ArgumentationScheme): The scheme that will
                be removed
        """
        self.schemes.remove(old_argumentation_scheme)

    def add_argumentation_scheme(self, new_argumentation_scheme: ArgumentationScheme):
        """Adds an argumentation scheme to the schemes list (schemes)

        Args:
            new_argumentation_scheme (ArgumentationScheme): The scheme that will
                be added
        """
        self.schemes.append(new_argumentation_scheme)

    def remove_domain_case(self, old_domain_cases: int):
        """Removes a domain case ID from the domain cases list
        (domain_cases_ids)

        Args:
            old_domain_cases (int): The ID that will be removed
        """
        self.domain_cases_ids.remove(old_domain_cases)

    def add_domain_case(self, new_domain_cases: int):
        """Adds a domain case ID from the domain cases list
        (domain_cases_ids)

        Args:
            new_domain_cases (int): The ID that will be added
        """
        self.domain_cases_ids.append(new_domain_cases)

    def remove_argument_case(self, old_argument_case: int):
        """Removes an argument case ID from the argument cases list
        (argument_cases_ids)

        Args:
            old_argument_case (int): The ID that will be removed
        """
        self.argument_cases_ids.remove(old_argument_case)

    def add_argument_case(self, new_argument_case: int):
        """Adds an argument case id (int) to the argument cases list
        (argument_cases_ids)

        Args:
            new_argument_case (int): The ID that will be added
        """
        self.argument_cases_ids.append(new_argument_case)

    def remove_dialogue_graph(self, old_dialog_graph: DialogueGraph):
        """Removes a dialogue graph from the dialogue graphs list
        (dialogue_graphs)

        Args:
            old_dialog_graph (DialogueGraph): The dialog graph that will be
                removed
        """
        self.dialogue_graphs.remove(old_dialog_graph)

    def add_dialogue_graph(self, new_dialog_graph: DialogueGraph):
        """Adds a dialogue graph to the dialogue graphs list (dialogue_graphs)

        Args:
            new_dialog_graph (DialogueGraph): The dialog graph that will be
                added
        """
        self.dialogue_graphs.append(new_dialog_graph)

    def merge_domain_cases_ids(self, new_ids: Sequence[int]):
        """Adds new domain cases IDs to the Justification skipping the duplicates

        Args:
            new_ids: The new IDs to be merged with
        """
        lists_operations.merge_lists_using_sets(self.domain_cases_ids, new_ids)
        # lists_operations.merge_lists_by_looping(self.domain_cases_ids, new_ids)

    def merge_argument_cases_ids(self, new_ids: Sequence[int]):
        """Adds new argument cases IDs to the Justification skipping the duplicates

        Args:
            new_ids: The new IDs to be merged with
        """
        lists_operations.merge_lists_using_sets(self.argument_cases_ids, new_ids)
        # lists_operations.merge_lists_by_looping(self.argument_cases_ids, new_ids)
