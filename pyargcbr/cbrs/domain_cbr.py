from pickle import load
from typing import Dict, List, ValuesView, Mapping, Sequence

from loguru import logger

from ..agents import similarity_algorithms as sim_algs
from ..agents.configuration import Configuration
from ..cbrs.cbr import CBR
from ..configuration.configuration_parameters import SimilarityType
from ..knowledge_resources.domain_case import DomainCase
from ..knowledge_resources.domain_context import DomainContext
from ..knowledge_resources.justification import Justification
from ..knowledge_resources.premise import Premise
from ..knowledge_resources.problem import Problem
from ..knowledge_resources.similar_domain_case import SimilarDomainCase


class DomainCBR(CBR):
    """This class implements the domain CBR."""
    index: int = -1

    def __init__(self, initial_file_path: str, storing_file_path: str, index: int):
        """This CBR stores domain knowledge of previously solved problems. It is
        used by the argumentative agent to generate and select the Position
        (solution) to defend in an argumentation dialogue.

        Args:
            initial_file_path (str): The path of the file to load the initial
                domain cases.
            storing_file_path (str): The path of the file to store the domain
                cases
            index (int): Identifier of the premise wich value will be used as a
                hash index. If not indexation is used, just set is value to -1
        """
        super().__init__(initial_file_path, storing_file_path)
        self.index = index
        self.load_case_base()

    def load_case_base(self):
        """Loads the case-base stored in the initial file path"""
        self.case_base = {}
        introduced = 0
        not_introduced = 0
        str_ids = ""
        with open(self.initial_file_path, 'rb') as fh:
            while True:
                try:
                    aux = load(fh)
                    if type(aux) == DomainCase:
                        a_case = aux
                        str_ids += str(a_case.solutions[0].conclusion.id) + " "
                        returned_value = self.add_case(a_case)
                        if returned_value:
                            introduced += 1
                        else:
                            not_introduced += 1
                except EOFError:
                    break
        logger.info(self.initial_file_path, "domain_cases: ", introduced + not_introduced,
                    "introduced: ", introduced, "not_introduced: ", not_introduced, "sols: ", str_ids)

    def retrieve_and_retain(self, dom_case: DomainCase, threshold: float) -> List[SimilarDomainCase]:
        """Retrieves the domain_cases that are in a range of similarity degree
        with the given one.

        Args:
            dom_case (DomainCase): The domain-case (representing a problem to
                solve) that needs a solution from the CBR
            threshold (float): The threshold of minimum degree of similarity of

        Returns:
            List[SimilarDomainCase]: A list with the domain cases
        """
        c = Configuration()
        similar_cases = self.get_most_similar(dom_case.problem.context.premises, threshold, c.domain_cbrs_similarity)
        if similar_cases:
            for similar_case in similar_cases:
                if similar_case.similarity < 1.0:
                    dom_case.solutions = similar_case.case.solutions
                    returned_value = self.add_case(dom_case)
                    if returned_value:
                        logger.info("New case Introduced")
                    else:
                        logger.info("New case NOT Introduced")
                else:
                    logger.info("New case NOT Introduced. Similar 1.0")

        return similar_cases

    def retrieve(self, premises: Dict[int, Premise], threshold: float) -> List[SimilarDomainCase]:
        """Retrieves the domain_cases that are in a range of similarity degree
        with the given premises.

        Args:
            premises (Dict[int, Premise]): The given premises
            threshold (float): The threshold that determines the range

        Returns:
            List[SimilarDomainCase]: The domain cases that fit in the range of
            similarity
        """
        # The parameter times_used can be also increased depending of the application domain
        c = Configuration()
        similar_cases = self.get_most_similar(premises, threshold, c.domain_cbrs_similarity)
        return similar_cases

    def add_case(self, new_case: DomainCase) -> bool:
        """Adds a new domain-case to domain case-base. Otherwise, if the same
        domain-case exists in the case-base, adds the relevant data to the
        existing domain-case.

        Args:
            new_case (DomainCase): :class:'DomainCase' that could be added.

        Returns:
            bool: True if the domain-case is added, else False.
        """
        main_premise_id = -1
        main_premise_value: str = ""
        cases: List[DomainCase] = []

        if self.index != -1:
            main_premise_value = new_case.problem.context.premises[self.index].content
            cases = self.case_base.get(main_premise_value, [])
        else:
            new_case_premises_list: List[int] = []
            for premise in new_case.problem.context.premises.values():
                new_case_premises_list.append(premise.id)
            new_case_premises_list = sorted(new_case_premises_list)
            main_premise_id = new_case_premises_list[0]
            cases = self.case_base.get(str(main_premise_id), [])

        if not cases:
            cases = [new_case]

            if main_premise_value:
                self.case_base[main_premise_value] = cases
            else:
                self.case_base[str(main_premise_id)] = cases
            return True

        found = False

        for current_case in cases:
            current_premises = current_case.problem.context.premises
            new_premises = new_case.problem.context.premises
            if len(current_premises) != len(new_premises):
                continue  # They do not have the same premises, we go to look the next one

            equal = True
            for case_prem in new_premises.values():
                prem_id = case_prem.id
                if prem_id not in current_premises.keys() \
                    or not current_premises[prem_id].content.lower() == case_prem.content.lower():
                    equal = False
                    break

            if equal:  # Same premises with same content
                # add the new solutions to the case if there are some
                for a_solution in new_case.solutions:
                    sol_found = False
                    for b_solution in current_case.solutions:
                        if b_solution.conclusion.id == a_solution.conclusion.id:
                            b_solution.times_used += a_solution.times_used
                            sol_found = True
                            break
                    if not sol_found:
                        a_solution.times_used = 1
                        current_case.add_solution(a_solution)

                found = True
                return False  # We do not introduce it because it is already in the case-base

        if not found:
            cases.append(new_case)
            return True

        return False

    def get_most_similar(self, premises: Dict[int, Premise], threshold: float, similarity_type: SimilarityType) \
        -> List[SimilarDomainCase]:
        """Gets the most similar domain cases that are in a range of similarity
        degree with the given premises The similarity algorithm is determined by
        a parameter.

        Args:
            premises (Mapping[int, Premise]): The given premises
            threshold (float): The threshold of minimum degree of similarity of
                the domain-cases to return.
            similarity_type (SimilarityType): A parameter to specify which
                similarity algorithm has to be used

        Returns:
            List[SimilarDomainCase]
        """
        candidate_cases = self.get_candidate_cases(premises)
        final_candidates: List[SimilarDomainCase] = []
        more_similar_candidates: List[SimilarDomainCase] = []

        if similarity_type == SimilarityType.NORMALIZED_EUCLIDEAN:
            final_candidates = sim_algs.normalized_euclidean_similarity(premises, candidate_cases)
        elif similarity_type == SimilarityType.WEIGHTED_EUCLIDEAN:
            final_candidates = sim_algs.weighted_euclidean_similarity(premises, candidate_cases)
        elif similarity_type == SimilarityType.NORMALIZED_TVERSKY:
            final_candidates = sim_algs.normalized_tversky_similarity(premises, candidate_cases)
        else:
            final_candidates = sim_algs.normalized_euclidean_similarity(premises, candidate_cases)

        for sim_case in final_candidates:
            if sim_case.similarity >= threshold:
                more_similar_candidates.append(sim_case)
            else:
                break
        return more_similar_candidates

    @staticmethod
    def get_premises_similarity(premises1: Dict[int, Premise], premises2: Dict[int, Premise]) -> float:
        """Obtains the similarity between two Dictionaries of premises using the
        similarity algorithm specified in the configuration of this class.

        Args:
            premises1 (Mapping[int, Premise]): Dictionary of premises 1.
            premises2 (Mapping[int, Premise]): Dictionary of premises 2.

        Returns:
            float: The value of the similarity.
        """
        c = Configuration()
        similarity_type = c.domain_cbrs_similarity
        cas = DomainCase(problem=Problem(DomainContext(premises2)), solutions=[],
                         justification=Justification())
        case_list: List[DomainCase] = []
        case_list.append(cas)
        final_candidates: List[SimilarDomainCase] = []

        if similarity_type == SimilarityType.NORMALIZED_EUCLIDEAN:
            final_candidates = sim_algs.normalized_euclidean_similarity(premises1, case_list)
        elif similarity_type == SimilarityType.WEIGHTED_EUCLIDEAN:
            final_candidates = sim_algs.weighted_euclidean_similarity(premises1, case_list)
        elif similarity_type == SimilarityType.NORMALIZED_TVERSKY:
            final_candidates = sim_algs.normalized_tversky_similarity(premises1, case_list)
        else:
            final_candidates = sim_algs.normalized_euclidean_similarity(premises1, case_list)

        return final_candidates[0].similarity

    def get_candidate_cases(self, premises: Mapping[int, Premise]) -> List[DomainCase]:
        """Gets a :class:'DomainCase' List with the domain_cases that fit the
        given premises

        Args:
            premises (Mapping[int, Premise]): Dictionary of premises that describes
                the problem

        Returns:
            class: 'DomainCase' List
        """
        candidate_cases: List[DomainCase] = []
        main_premise_id: int = -1
        main_premise_value: str = ''

        if self.index != -1:
            main_premise_value = premises[self.index].content
            candidate_cases = self.case_base.get(main_premise_value, [])
            if not candidate_cases:
                candidate_cases = []
        else:
            new_case_premises_list: List[int] = []
            for premise in premises.values():
                new_case_premises_list.append(premise.id)
            new_case_premises_list = sorted(new_case_premises_list)  # for sorted '15' < '2'
            for premise_id in new_case_premises_list:
                main_premise_id = premise_id
                dom_cases = self.case_base.get(str(main_premise_id))
                if dom_cases:
                    candidate_cases += dom_cases
        return candidate_cases

    def do_cache(self):
        super().do_cache()

    def do_cache_inc(self):
        super().do_cache_inc()

    def get_all_cases(self) -> ValuesView[Sequence[DomainCase]]:
        return super().get_all_cases()

    def get_all_cases_list(self) -> Sequence[DomainCase]:
        return super().get_all_cases_list()
