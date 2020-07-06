from dataclasses import dataclass

from knowledge_resources.domain_case import DomainCase
from knowledge_resources.similar_case import SimilarCase


@dataclass
class SimilarDomainCase(SimilarCase):
    """Structure to store the degree of similarity of a domain case"""
    case: DomainCase
