from typing import List

from knowledge_resources.case import Case
from knowledge_resources.justification import Justification
from knowledge_resources.problem import Problem
from knowledge_resources.solution import Solution


class DomainCase(Case):
    """Implementation of the concept DomainCase"""
    def __init__(self, problem: Problem = Problem(), solutions: List[Solution] = [],
                 justification: Justification = Justification()):
        """DomainCase is a specialization of Case"""
        self.problem = problem
        self.solutions = solutions
        self.justification = justification

    def remove_solution(self, old_solution: Solution):
        """Removes a solution from the solutions list (solutions)

        Args:
            old_solution (Solution): The solution that will be removed
        """
        self.solutions.remove(old_solution)

    def add_solution(self, new_solution: Solution):
        """Adds a solution to the solutions list (solutions)

        Args:
            new_solution (Solution): The solution that will be added
        """
        self.solutions.append(new_solution)
