from dataclasses import dataclass

from knowledge_resources.argument_case import ArgumentCase


@dataclass
class SimilarArgumentCase:
    argument_case: ArgumentCase
    suitability: float

    def my_cmp(self, other):
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
