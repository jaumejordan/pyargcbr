from dataclasses import dataclass

from knowledge_resources.domain_case import DomainCase


@dataclass
class SimilarDomainClass:
    caseb: DomainCase
    similarity: float
