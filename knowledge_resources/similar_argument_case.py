from dataclasses import dataclass

from knowledge_resources.argument_case import ArgumentCase


@dataclass
class SimilarArgumentCase:
    """Structure to store the degree of similarity of an argument case"""
    argument_case: ArgumentCase
    suitability: float

    def my_cmp(self, other: SimilarArgumentCase) -> int:
        """Comparator used to calculate all the comparison functions for the
        SimilarArgumentCase objects

        Args:
            other (SimilarArgumentCase): The other similar argument case object
                to compare with

        Returns:
            A negative integer if the other similar argument case object is
            greater, 0 if both objects are equals and a positive integer
            otherwise
        """
        return round(self.suitability * 100000 - other.suitability * 100000)

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
