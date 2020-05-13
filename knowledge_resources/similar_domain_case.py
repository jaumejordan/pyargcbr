from dataclasses import dataclass

from knowledge_resources.domain_case import DomainCase


@dataclass
class SimilarDomainCase:
    """Structure to store the degree of similarity of a domain case"""
    caseb: DomainCase
    similarity: float

    def my_cmp(self, other:SimilarDomainCase) -> int:
        """Comparator used to calculate all the comparison functions for the
        SimilarDomainCase objects

        Args:
            other (SimilarDomainCase): The other similar domain case object
                to compare with

        Returns:
            int: A negative integer if the other similar domain case object is
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
