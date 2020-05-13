from dataclasses import dataclass
from typing import List, Union, Type, Sequence

from knowledge_resources.case_component import CaseComponent
from knowledge_resources.justification import Justification
from knowledge_resources.problem import Problem
from knowledge_resources.solution import Solution


@dataclass
class Case:
    """Implementation of the concept Case"""
    problem: Problem
    solutions: Union[List[Solution], Solution]
    justification: Justification
    id: int = -1
    # TODO Maybe using datetime is a better idea -> It is not necessary (see metrics.py)
    creation_date: str = ""
