from dataclasses import dataclass
from pickle import load
from typing import Dict, List
from agents.configuration import Configuration
import agents.similarity_algorithms as sim_algs
from configuration.configuration_parameters import SimilarityType
from knowledge_resources.domain_case import DomainCase
from knowledge_resources.premise import Premise
from knowledge_resources.similar_domain_case import SimilarDomainCase

"""
 This class implements the domain CBR. This CBR stores domain knowledge of
 previously solved problems. It is used by the argumentative agent to generate
 and select the {@link Position} (solution) to defend in an argumentation
 dialogue.
"""
@dataclass
class DomainCBR:
    # KEY: str - VALUE: list[DomainCase]
    domain_cb: Dict[str, List[DomainCase]]
    file_path: str
    storing_file_path: str
    index: int = -1

    def __init__(self, file_path: str, storing_file_path:str, index: int):
        self.file_path = file_path
        self.storing_file_path = storing_file_path
        self.index = index
        self.load_case_base()

    def load_case_base(self):
        self.domain_cb = {}
        introduced = 0
        not_introduced = 0
        str_ids = ""
        with open(self.storing_file_path) as fh:
            aux = load(fh)
            while aux:
                if type(aux) == DomainCase:
                    a_case = aux
                    str_ids += a_case.solutions[0].conclusion.id + " "
                    returned_value = self.add_case(a_case)
                    if returned_value:
                        introduced += 1
                    else:
                        not_introduced += 1
                aux = load(fh)

        print(self.file_path, "domain_cases: ", introduced + not_introduced,
              "introduced: ", introduced, "not_introduced: ", not_introduced, "sols: ", str_ids)

    def retrieve_and_retain(self, dom_case: DomainCase, threshold: float) -> List[SimilarDomainCase]:
        c = Configuration()
        similar_cases = self.get_most_similar(dom_case.problem.context.premises, threshold, c.domain_cbrs_similarity)
        if not similar_cases:
            for similar_case in similar_cases:
                if similar_case.similarity < 1.0:
                    dom_case.solutions = similar_case.caseb.solutions
                    returned_value = self.add_case(dom_case)
                    if returned_value:
                        print("New case Introduced")
                    else:
                        print("New case NOT Introduced")
                else:
                    print("New case NOT Introduced. Similar 1.0")

        return similar_cases

    def add_case(self, new_case:DomainCase):
        main_premise_id = -1
        main_premise_value = str
        cases = List[DomainCase]

        if self.index != -1:
            main_premise_value = new_case.problem.context.premises[self.index].content
            cases = self.domain_cb[main_premise_value]
        else:
            new_case_premises_list: List[int] = []
            for premise in new_case.problem.context.premises.values():
                new_case_premises_list.append(premise.id)
            new_case_premises_list = sorted(new_case_premises_list)
            main_premise_id = new_case_premises_list[0]
            cases = self.domain_cb[str(main_premise_id)] #TODO validate this line

        if not cases:
            cases = []
            cases.append(new_case)

            if main_premise_value:
                self.domain_cb[main_premise_value] = cases
            else:
                self.domain_cb[str(main_premise_id)] = cases
            return True

        found = False

    def get_most_similar(self, premises: Dict[int, Premise], threshold: float, similarity_type: SimilarityType) -> List[SimilarDomainCase]:
        candidate_cases = self.get_candidate_cases(premises)
        final_candidates = List[SimilarDomainCase]
        more_similar_candidates = List[SimilarDomainCase]

        if similarity_type == SimilarityType.NORMALIZED_EUCLIDEAN:
            sim_algs.normalized_euclidean_similarity(premises, candidate_cases)
        elif similarity_type == SimilarityType.WEIGHTED_EUCLIDEAN:
            sim_algs.weighted_euclidean_similarity(premises, candidate_cases)
        elif similarity_type == SimilarityType.NORMALIZED_TVERSKY:
            sim_algs.normalized_tversky_similarity(premises, candidate_cases)
        else:
            sim_algs.normalized_euclidean_similarity(premises, candidate_cases)

        for sim_case in final_candidates:
            if sim_case.similarity >= threshold:
                more_similar_candidates.append(sim_case)
            else:
                break
        return more_similar_candidates

    def get_candidate_cases(self, premises: Dict[int, Premise]) -> List[DomainCase]:
        candidate_cases: List[DomainCase] = []
        main_premise_id = -1
        main_premise_value = str

        if self.index != -1:
            main_premise_value = premises[self.index].content
            candidate_cases = self.domain_cb[main_premise_value]
            if not candidate_cases:
                candidate_cases = []
        else:
            new_case_premises_list = []
            for premise in premises.keys():
                new_case_premises_list.append(premise)
            new_case_premises_list = sorted(new_case_premises_list)
            for premise_id in new_case_premises_list:
                main_premise_id = premise_id
                dom_cases = self.domain_cb[str(main_premise_id)] #TODO validate this line
                if dom_cases:
                    candidate_cases.append(dom_cases)
        return candidate_cases
