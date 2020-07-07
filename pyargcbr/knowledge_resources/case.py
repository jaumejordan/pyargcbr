from dataclasses import dataclass
from typing import List, Union

from .justification import Justification
from .problem import Problem
from .solution import Solution


@dataclass
class Case:
    """Implementation of the concept Case"""
    problem: Problem
    solutions: Union[List[Solution], Solution]
    justification: Justification
    id: int = -1
    creation_date: str = ""
