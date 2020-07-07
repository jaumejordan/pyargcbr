from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence, List

from ..agents.metrics import do_dist as compare


@dataclass
class Premise:
    """Implementation of the concept Premise"""
    id: int = -1
    name: str = field(default="", compare=False)
    content: str = field(default="", compare=False)

    def my_cmp(self, other: Premise) -> int:
        """Comparator used to calculate all the comparison functions for the
        Premise objects

        Args:
            other (Premise): The other premise to compare with

        Returns:
            int: A negative integer if the other premise is greater, 0 if both
            premises are equals and a positive integer otherwise
        """
        return self.id - other.id

    def __lt__(self, other):
        return self.my_cmp(other) < 0

    def __gt__(self, other):
        return self.my_cmp(other) > 0

    def __eq__(self, other):
        res = self.my_cmp(other) == 0
        res *= compare(self.name, other.name) == 0
        res *= compare(self.content, other.content) == 0
        return res

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    @staticmethod
    def merge_premises_lists(target_list: List[Premise], new_premises_list: Sequence[Premise]):
        """Merge two lists of premises into one. The duplicates (same ID and
        content) are removed

        Args:
            target_list (List[Premise]): The first list of premises and the one
                that will be modified
            new_premises_list (Sequence[Premise])): The list of premises to be
                merged with

        Returns:
            None: The target list is passed by reference, so it is modified
            directly
        """
        for premise2 in new_premises_list:
            add_premise = True
            for premise1 in target_list:
                if (premise2.id == premise1.id
                    and premise2.content == premise1.content):
                    add_premise = False
                    break
            if add_premise:
                target_list.append(premise2)
