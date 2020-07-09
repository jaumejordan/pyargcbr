from math import sqrt
from typing import Dict, List

from .metrics import do_dist
from ..knowledge_resources.domain_case import DomainCase
from ..knowledge_resources.premise import Premise
from ..knowledge_resources.similar_domain_case import SimilarDomainCase


def normalized_euclidean_similarity(premises: Dict[int, Premise], candidate_cases: List[DomainCase]) \
    -> List[SimilarDomainCase]:
    """
    Returns a list of the candidate domain-cases with a similarity degree to the given domain-cases.
    The similarity is calculated using normalized Euclidean distance among the premises.

    :param premises: Dict with the premises to calculate the similarity with the candidate domain_cases
    :param candidate_cases: The domain-cases that can be similar to the domain-case to solve
    :return: A similar domain-case's list with the candidates ordered by its similarity degree [0.0...1.0]
    """
    num_cases = len(candidate_cases)
    accum_dist = [0] * num_cases

    for premise in premises.values():
        max_dist = 0.0
        index = 0
        # temporal vector of distances per attribute: key: case object, value: distance
        aux_dist: List[float] = [1.0] * num_cases
        # marks vector of max distances: key: case object, value: true/false
        # This means the ones with the value True associated will have a final similarity value of 1
        max_dist_vec: List[bool] = [False] * num_cases

        for candidate in candidate_cases:
            candidate_premise = candidate.problem.context.premises.get(premise.id, None)
            if candidate_premise:
                aux_dist[index] = do_dist(premise.content, candidate_premise.content)
            else:
                max_dist_vec[index] = True  # The attribute does not exist in the retrieved case

            # If the new calculated similarity is the greatest we update the value of the max
            if aux_dist[index] > max_dist:
                max_dist = aux_dist[index]
            index += 1

        # Now we normalize the distances -> [0.0...1.0]
        for index in range(num_cases):
            if not max_dist:
                aux_dist[index] = 0
            elif max_dist_vec[index]:
                aux_dist[index] = 1
            else:
                aux_dist[index] /= max_dist

            aux_dist[index] += aux_dist[index]
            accum_dist[index] += aux_dist[index]

    final_candidates: List[SimilarDomainCase] = []
    index = 0
    for candidate in candidate_cases:
        for candidate_premise in candidate.problem.context.premises.values():
            if not premises.get(candidate_premise.id, None):  # Not found
                accum_dist[index] += 1

        similarity: float = 1 / (sqrt(accum_dist[index]) + 1)
        final_candidates.append(SimilarDomainCase(candidate, similarity))
        index += 1

    return sorted(final_candidates, reverse=True)


def weighted_euclidean_similarity(premises: Dict[int, Premise], candidate_cases: List[DomainCase]) \
    -> List[SimilarDomainCase]:
    """
    Returns a list of the candidate domain-cases with a similarity degree to the given domain-cases.
    The similarity is calculated using weighted Euclidean distance among the premises.

    :param premises: Dict with the premises to calculate the similarity with the candidate domain_cases
    :param candidate_cases: The domain-cases that can be similar to the domain-case to solve
    :return: A similar domain-case's list with the candidates ordered by its similarity degree [0.0...1.0]
    """
    final_candidates: List[SimilarDomainCase] = []
    for candidate in candidate_cases:
        distance = 0.0
        weight: List[float] = [1.0] * len(premises)
        attribute = 0

        for case_premise in premises.values():
            my_dist = 1.0

            candidate_premise = candidate.problem.context.premises.get(case_premise.id, None)
            if candidate_premise:
                my_dist = do_dist(case_premise.content, candidate_premise.content)

            weight[attribute] *= weight[attribute]
            my_dist += my_dist
            distance += weight[attribute] * my_dist
            attribute += 1

        for candidate_premise in candidate.problem.context.premises.values():
            domain_case_premise = premises.get(candidate_premise.id, None)
            if not domain_case_premise:  # Not found
                distance += 1

        similarity: float = 1 / (sqrt(distance) + 1)
        final_candidates.append(SimilarDomainCase(candidate, similarity))

    return sorted(final_candidates, reverse=True)


def normalized_tversky_similarity(premises: Dict[int, Premise], candidate_cases: List[DomainCase]) \
    -> List[SimilarDomainCase]:
    num_cases = len(candidate_cases)
    common_at: List[float] = [0.0] * num_cases
    different_at: List[float] = [0.0] * num_cases
    distinct_at: List[float] = [0.0] * num_cases

    for premise in premises.values():
        max_dist = 0.0
        index = 0
        # temporal vector of distances per attribute: key: case object, value: distance
        aux_dist: List[float] = [1.0] * num_cases
        # marks vector of max distances: key: case object, value: true/false
        # This means the ones with the value True associated will have a final similarity value of 1
        max_dist_vec: List[bool] = [False] * num_cases

        for candidate in candidate_cases:
            candidate_premise = candidate.problem.context.premises.get(premise.id, None)
            if candidate_premise:
                aux_dist[index] = do_dist(premise.content, candidate_premise.content)
            else:
                max_dist_vec[index] = True  # The attribute does not exist in the retrieved case

            # If the new calculated similarity is the greatest we update the value of the max
            if aux_dist[index] > max_dist:
                max_dist = aux_dist[index]
            index += 1

        # Now we normalize the distances
        for index in range(num_cases):
            if max_dist == 0:
                aux_dist[index] = 0
            else:
                if max_dist_vec[index]:
                    aux_dist[index] = 1
                else:
                    aux_dist[index] /= max_dist

                if aux_dist[index] < 0.05:
                    common_at[index] += 1
                else:
                    different_at[index] += 1

    final_candidates: List[SimilarDomainCase] = []
    index = 0
    for candidate in candidate_cases:
        for candidate_premise in candidate.problem.context.premises.values():
            if not premises.get(candidate_premise.id, None):  # Not found
                distinct_at[index] += 1

        similarity: float = common_at[index] / (common_at[index] + different_at[index] + distinct_at[index])
        final_candidates.append(SimilarDomainCase(candidate, similarity))
        index += 1

    return sorted(final_candidates, reverse=True)
