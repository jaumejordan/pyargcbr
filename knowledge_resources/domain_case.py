from dataclasses import dataclass, field
from knowledge_resources.case import Case
from knowledge_resources.justification import Justification
from knowledge_resources.problem import Problem
from knowledge_resources.solution import Solution


@dataclass
class DomainCase(Case):
    problem: Problem = field(default=Problem())
    # Solution
    solutions: list = field(default=[])
    justification: Justification = Justification()

    def remove_solution(self, old_solution: Solution):
        self.solutions.remove(old_solution)

    def add_solution(self, new_solution: Solution):
        self.solutions.append(new_solution)
