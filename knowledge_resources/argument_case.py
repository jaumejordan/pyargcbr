from dataclasses import dataclass, field

from knowledge_resources.argument_problem import ArgumentProblem
from knowledge_resources.argument_solution import ArgumentSolution


@dataclass
class ArgumentCase:
    problem: ArgumentProblem = field(default=ArgumentProblem())
    solution: ArgumentSolution = field(default=ArgumentSolution())
