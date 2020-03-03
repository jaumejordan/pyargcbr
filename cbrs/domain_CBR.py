from dataclasses import dataclass
from pickle import load, dump
from typing import Dict, List, ValuesView
from agents.configuration import Configuration
import agents.similarity_algorithms as sim_algs
from configuration.configuration_parameters import SimilarityType
from knowledge_resources.domain_case import DomainCase
from knowledge_resources.domain_context import DomainContext
from knowledge_resources.justification import Justification
from knowledge_resources.premise import Premise
from knowledge_resources.problem import Problem
from knowledge_resources.position import Position
from knowledge_resources.similar_domain_case import SimilarDomainCase


# TODO check about https://www.jetbrains.com/help/pycharm/using-docstrings-to-specify-types.html
def save_object(obj, file_name: str):
    """
    Saves an object in the file corresponding to the path; it's incremental.

    Parameters:
        obj (Object): The object that will be stored.
        file_name: The path to the file where the object will be stored.
    """
    with open(file_name, 'wb') as fh:
        dump(obj, fh)


class DomainCBR:
    """
     This class implements the domain CBR.

     This CBR stores domain knowledge of previously solved problems. It is used by the argumentative agent to generate
     and select the :class:'Position' (solution) to defend in an argumentation dialogue.

     Attributes:
         domain_cb (Dict[str, List[DomainCase]]): .
         file_path (str): The path of the file to load the initial domain-cases.
         storing_file_path (str): The path of the file where the final domain-cases will be stored.
         index (int): The identifier of the premise which value will be used as a hash index; -1 means indexation is not used
    """
    domain_cb: Dict[str, List[DomainCase]]
    file_path: str
    storing_file_path: str
    index: int = -1

    def __init__(self, file_path: str, storing_file_path: str, index: int):
        self.file_path = file_path
        self.storing_file_path = storing_file_path
        self.index = index
        self.load_case_base()

    def load_case_base(self):
        """
        Loads the case-base stored in the initial file path.
        """
        self.domain_cb = {}
        introduced = 0
        not_introduced = 0
        str_ids = ""
        with open(self.file_path, 'rb') as fh:
            while True:
                try:
                    aux = load(fh)
                    print(type(aux))
                    if type(aux) == DomainCase:
                        a_case = aux
                        str_ids += a_case.solutions[0].conclusion.id + " "
                        returned_value = self.add_case(a_case)
                        if returned_value:
                            introduced += 1
                        else:
                            not_introduced += 1
                except EOFError:
                    break
        print(self.file_path, "domain_cases: ", introduced + not_introduced,
              "introduced: ", introduced, "not_introduced: ", not_introduced, "sols: ", str_ids)

    def retrieve_and_retain(self, dom_case: DomainCase, threshold: float) -> List[SimilarDomainCase]:
        """
        Retrieves the domain_cases that are in a range of similarity degree with the given one.

        Parameters:
            dom_case (DomainCase): The domain-case (representing a problem to solve) that needs a solution from the CBR
            threshold (float): The threshold of minimum degree of similarity of the domain-cases to return.

        Returns:
            List of :class:'SimilarDomainCase'.
        """
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

    def retrieve(self, premises: Dict[int, Premise], threshold: float) -> List[SimilarDomainCase]:
        """
        Retrieves the domain_cases that are in a range of similarity degree with the given premises.

        Parameters:
            premises (Dict[int, Premise]): Dictionary of premises that describe the problem to solve.
            threshold (float): The threshold of minimum degree of similarity of the domain-cases to return.

        Returns:
            List of :class:'SimilarDomainCase'.
        """
        # TODO The parameter times_used can be also increased depending of the application domain
        c = Configuration()
        similar_cases = self.get_most_similar(premises, threshold, c.domain_cbrs_similarity)
        return similar_cases

    def add_case(self, new_case: DomainCase) -> bool:
        """
        Adds a new domain-case to domain case-base. Otherwise, if the same domain-case exists in the case-base, adds
        the relevant data to the existing domain-case.

        Parameters:
            new_case(DomainCase): :class:'DomainCase' that could be added.

        Returns:
            True if the domain-case is added, else False.
        """
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
            cases = self.domain_cb[str(main_premise_id)]  # TODO validate this line

        if not cases:
            cases = [new_case]

            if main_premise_value:
                self.domain_cb[main_premise_value] = cases
            else:
                self.domain_cb[str(main_premise_id)] = cases
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
                            b_solution.times_used += a_solution.times_used  # TODO check if this is now correct (in Java was different)
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

    def get_most_similar(self, premises: Dict[int, Premise], threshold: float, similarity_type: SimilarityType) -> List[
        SimilarDomainCase]:
        """
        Gets the most similar domain-cases that are in a range of similarity degree with the given premises
        The similarity algorithm is determined by an integer parameter.

        Parameters:
            threshold (float): The threshold of minimum degree of similarity of the domain-cases to return.
            similarity_type (SimilarityType): A :class:'SimilarDomainCase' to specify which similarity algorithm has to
            be used.

        Returns:
            List of :class:'SimilarDomainCase'.
        """
        candidate_cases = self.get_candidate_cases(premises)
        final_candidates = List[SimilarDomainCase]
        more_similar_candidates = List[SimilarDomainCase]

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

    @staticmethod  # TODO is it useful for this method to be static?
    def get_premises_similarity(premises1: Dict[int, Premise], premises2: Dict[int, Premise]):
        """
         Obtains the similarity between two Dictionaries of premises using the similarity algorithm specified in the
         configuration of this class.

        Parameters:
            premises1 (Dict[int, Premise]): Dictionary of premises 1.
            premises2 (Dict[int, Premise]): Dictionary of premises 2.

        Returns:
            The value of the similarity.
        """
        c = Configuration()
        similarity_type = c.domain_cbrs_similarity
        cas = DomainCase(problem=Problem(DomainContext(premises2)), solutions=[],
                         justification=Justification())
        case_list = List[DomainCase]
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

    def do_cache(self):
        """
        Stores the current domain-cases case-base to the storing file path.
        """
        with open(self.storing_file_path) as f:
            f.write(None)  # TODO This is supposed to reset the file
        self.do_cache_inc()

    def do_cache_inc(self):
        """
        Stores the current domain-cases case-base to the storing file path without removing the previous objects.
        """
        for a_case in self.get_all_cases():
            save_object(a_case, self.storing_file_path)

    def get_all_cases(self) -> ValuesView[List[DomainCase]]:  # TODO What is ValuesView? D:
        """
        Returns all the cases.

        Returns:
            ValuesView[List[DomainCase]].
        """
        return self.domain_cb.values()

    def get_all_cases_list(self) -> List[DomainCase]:
        """
        Returns all the cases.

        Returns:
            List[DomainCase].
        """
        cases: List[DomainCase] = []
        for list_cases in self.get_all_cases():
            cases += list_cases
        return cases
    # TODO get_all_cases_list, get_all_cases and get_all_cases_vector might be implemented as one

    def get_candidate_cases(self, premises: Dict[int, Premise]) -> List[DomainCase]:
        """
        Gets a :class:'DomainCase' List with the domain_cases that fit the given premises

        Parameters:
            premises (Dict[int, Premise]): Dictionary of premises that describes the problem

        Returns:
            :class:'DomainCase' List
        """
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
                dom_cases = self.domain_cb[str(main_premise_id)]  # TODO validate this line
                if dom_cases:
                    candidate_cases.append(dom_cases)
        return candidate_cases
