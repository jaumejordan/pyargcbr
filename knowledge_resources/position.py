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
