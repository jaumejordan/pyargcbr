from typing import Mapping, List
from knowledge_resources.domain_case import DomainCase
from knowledge_resources.premise import Premise
from knowledge_resources.similar_domain_case import SimilarDomainCase


def normalized_euclidean_similarity(premises: Mapping[int, Premise], candidate_cases: List[DomainCase]) \
    -> List[SimilarDomainCase]:
    pass

def weighted_euclidean_similarity(premises: Mapping[int, Premise], candidate_cases: List[DomainCase]) \
    -> List[SimilarDomainCase]:
    pass

def normalized_tversky_similarity(premises: Mapping[int, Premise], candidate_cases: List[DomainCase]) \
    -> List[SimilarDomainCase]:
    pass
