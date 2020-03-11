from dataclasses import dataclass
from typing import Dict, List

from knowledge_resources.domain_case import DomainCase
from knowledge_resources.premise import Premise
from knowledge_resources.solution import Solution

@dataclass
class Position:
    agent_id: str
    dialogue_id: str
    solution: Solution
    premises: Dict[int, Premise]
    domain_cases: List[DomainCase]
    domain_case_similarity: float
    arg_suitability_factor: float
    final_suitability: float
    times_accepted: int

    def remove_domain_cases(self, old_domain_case: DomainCase):
        self.domain_cases.remove(old_domain_case)

    def add_domain_cases(self,new_domain_case: DomainCase):
        self.domain_cases.append(new_domain_case)

    def my_cmp(self, other):
        return round(other.final_suitability * 100000 - self.final_suitability * 100000)

    def __lt__(self, other):
        return self.my_cmp(other) < 0

    def __gt__(self, other):
        return self.my_cmp(other) > 0

    def __eq__(self, other):
        return self.my_cmp(other) == 0

    def __le__(self, other):
        return self.my_cmp(other) <= 0

    def __ge__(self, other):
        return self.my_cmp(other) >= 0

    def __ne__(self, other):
        return self.my_cmp(other) != 0
