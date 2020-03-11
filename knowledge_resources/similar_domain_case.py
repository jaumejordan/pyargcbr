from dataclasses import dataclass

from knowledge_resources.domain_case import DomainCase


@dataclass
class SimilarDomainCase:
    caseb: DomainCase
    similarity: float

    def my_cmp(self, other):
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
