from dataclasses import dataclass

from knowledge_resources.argument_case import ArgumentCase


@dataclass
class SimilarArgumentCase:
    argument_case: ArgumentCase
    suitability: float

    def __cmp__(self, other):
        return round(self.suitability * 100000 - other.suitability * 100000)
