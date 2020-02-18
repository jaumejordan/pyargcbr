from dataclasses import dataclass

from knowledge_resources.domain_case import DomainCase


@dataclass
class SimilarDomainCase:
    caseb: DomainCase
    similarity: float

    def __cmp__(self, other):
        return round(self.similarity * 100000 - other.similarity * 100000)

