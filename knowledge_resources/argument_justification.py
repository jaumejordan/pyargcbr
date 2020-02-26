from dataclasses import dataclass, field
from typing import List
from knowledge_resources.argumentation_scheme import ArgumentationScheme
from knowledge_resources.dialogue_graph import DialogueGraph
from knowledge_resources.justification import Justification


@dataclass
class ArgumentJustification(Justification):
    domain_cases_ids: List[int] = field(default_factory=lambda:[])
    argument_cases_ids: List[int] = field(default_factory=lambda:[])
    schemes: List[ArgumentationScheme] = field(default_factory=lambda:[])
    dialogue_graphs: List[DialogueGraph] = field(default_factory=lambda:[])

    def remove_argumentation_scheme(self, old_argumentation_scheme: ArgumentationScheme):
        self.schemes.remove(old_argumentation_scheme)

    def add_argumentation_case(self, new_argumentation_scheme: ArgumentationScheme):
        self.schemes.append(new_argumentation_scheme)

    def remove_domain_case(self, old_domain_cases: int):
        self.domain_cases_ids.remove(old_domain_cases)

    def add_domain_case(self, new_domain_cases: int):
        self.domain_cases_ids.append(new_domain_cases)

    def remove_argument_case(self, old_argument_case: int):
        self.argument_cases_ids.remove(old_argument_case)

    def add_argument_case(self, new_argument_case: int):
        self.argument_cases_ids.append(new_argument_case)

    def remove_dialogue_graph(self, old_dialog_graph: DialogueGraph):
        self.dialogue_graphs.remove(old_dialog_graph)

    def add_dialogue_graph(self, new_dialog_graph: DialogueGraph):
        self.dialogue_graphs.append(new_dialog_graph)
