from __future__ import annotations

from dataclasses import dataclass

from .case import Case


@dataclass
class SimilarCase:
    """Structure to store the degree of similarity of a case"""
    case: Case
    similarity: float

    def my_cmp(self, other: SimilarCase) -> int:
        """Comparator used to calculate all the comparison functions for the
        SimilarCase objects

        Args:
            other (SimilarCase): The other similar argument case object
                to compare with

        Returns:
            A negative integer if the other similar case object is
            greater, 0 if both objects are equals and a positive integer
            otherwise
        """
        return round(self.similarity * 100000 - other.similarity * 100000)

    def __lt__(self, other):
        return self.my_cmp(other) < 0

    def __gt__(self, other):
        return self.my_cmp(other) > 0

    def __eq__(self, other):
        return self.my_cmp(other) == 0

    def __le__(self, other):
        return self.my_cmp(other) <= 0

    def __ge__(self, other):
        return self.my_cmp(other) >= 0

    def __ne__(self, other):
        return self.my_cmp(other) != 0
