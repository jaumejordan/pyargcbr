from typing import Mapping
from dataclasses import dataclass, field
from knowledge_resources.context import Context
from knowledge_resources.premise import Premise


@dataclass
class DomainContext(Context):
    premises: Mapping[int, Premise] = field(default_factory=dict)

    def remove_premise(self, old_premise: Premise):
        del self.premises[old_premise.id]

    def set_premises_from_list(self, new_premises: list[Premise]):
       for new_premise in new_premises:
        self.premises[new_premise.id] = new_premise
