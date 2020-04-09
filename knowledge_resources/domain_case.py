from dataclasses import dataclass, field
from typing import List
from knowledge_resources.case import Case
from knowledge_resources.justification import Justification
from knowledge_resources.problem import Problem
from knowledge_resources.solution import Solution


class DomainCase(Case):
    def __init__(self):
        self.problem = Problem()
        self.solutions = []
        self.justification = Justification()

    def remove_solution(self, old_solution: Solution):
        self.solutions.remove(old_solution)

    def add_solution(self, new_solution: Solution):
        self.solutions.append(new_solution)
