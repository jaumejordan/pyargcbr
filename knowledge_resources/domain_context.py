from typing import Dict
from dataclasses import dataclass, field
from knowledge_resources.context import Context
from knowledge_resources.premise import Premise


@dataclass
class DomainContext(Context):
    premises: Dict[int, Premise] = field(default_factory=lambda:{})

    def remove_premise(self, old_premise: Premise):
        del self.premises[old_premise.id]

    def add_premise(self, new_premise: Premise):
        self.premises[new_premise.id] = new_premise

    def set_premises_from_list(self, new_premises: list):
        for new_premise in new_premises:
            self.premises[new_premise.id] = new_premise
