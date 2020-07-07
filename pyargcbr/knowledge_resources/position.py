from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .domain_case import DomainCase
from .premise import Premise
from .solution import Solution


@dataclass
class Position:
    """Implementation of the concept Position"""
    agent_id: str
    dialogue_id: str
    solution: Solution
    premises: Optional[Dict[int, Premise]]
    domain_cases: Optional[List[DomainCase]]
    domain_case_similarity: float
    arg_suitability_factor: Optional[float] = None
    final_suitability: Optional[float] = None
    times_accepted: int = 0

    def remove_domain_cases(self, old_domain_case: DomainCase):
        """Removes a domain case from the domain cases list (domain_cases)

        Args:
            old_domain_case (DomainCase): The domain case that will be removed
        """
        self.domain_cases.remove(old_domain_case)

    def add_domain_cases(self, new_domain_case: DomainCase):
        """Adds a domain case to the domain cases list (domain_cases)

        Args:
            new_domain_case (DomainCase): The domain case that will be added
        """
        self.domain_cases.append(new_domain_case)

    def my_cmp(self, other: Position) -> int:
        """Comparator used to calculate all the comparison functions for the
        Position objects

        Args:
            other (Position): The other position to compare with

        Returns:
            int: A negative integer if the other position is greater, 0 if both
            positions are equals and a positive integer otherwise
        """
        return round(other.final_suitability * 100000 - self.final_suitability * 100000)

    def __lt__(self, other) -> bool:
        return self.my_cmp(other) < 0

    def __gt__(self, other) -> bool:
        return self.my_cmp(other) > 0

    def __eq__(self, other) -> bool:
        return self.my_cmp(other) == 0

    def __le__(self, other) -> bool:
        return self.my_cmp(other) <= 0

    def __ge__(self, other) -> bool:
        return self.my_cmp(other) >= 0

    def __ne__(self, other) -> bool:
        return self.my_cmp(other) != 0
