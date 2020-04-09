from dataclasses import dataclass
from typing import List, Union, Type

from knowledge_resources.justification import Justification
from knowledge_resources.problem import Problem
from knowledge_resources.solution import Solution


@dataclass
class Case:
    problem: Type[Problem]
    solutions: Union[List[Type[Solution]], Type[Solution]]
    justification: Type[Justification]
    id: int = -1
    # TODO Maybe using datetime is a better idea -> It is not necessary (see metrics.py)
    creation_date: str = ""
