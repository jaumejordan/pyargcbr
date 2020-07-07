from dataclasses import dataclass

from .domain_case import DomainCase
from .similar_case import SimilarCase


@dataclass
class SimilarDomainCase(SimilarCase):
    """Structure to store the degree of similarity of a domain case"""
    case: DomainCase
