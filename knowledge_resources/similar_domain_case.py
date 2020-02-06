from dataclasses import dataclass

from knowledge_resources.domain_case import DomainCase


@dataclass
class SimilarDomainCase:
    caseb: DomainCase
    similarity: float
