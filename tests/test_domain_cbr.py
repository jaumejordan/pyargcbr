#!/usr/bin/env python

"""Tests for `pyargcbr` package."""
import os
from typing import List, Dict

import pytest

from pyargcbr.agents.metrics import levenshtein_distance as cmp
from pyargcbr.cbrs.domain_cbr import DomainCBR
from pyargcbr.knowledge_resources.domain_case import DomainCase
from pyargcbr.knowledge_resources.domain_context import DomainContext
from pyargcbr.knowledge_resources.justification import Justification
from pyargcbr.knowledge_resources.premise import Premise
from pyargcbr.knowledge_resources.problem import Problem
from pyargcbr.knowledge_resources.similar_domain_case import SimilarDomainCase


def similar_domain_case_comparison(case1: SimilarDomainCase, case2: SimilarDomainCase):
    premises1 = list(case1.case.problem.context.premises.values())
    premises2 = list(case2.case.problem.context.premises.values())
    solutions1 = case1.case.solutions
    solutions2 = case2.case.solutions
    if case1.similarity == case2.similarity \
        and cmp(case1.case.justification.description, case2.case.justification.description) == 0 \
        and len(premises1) == len(premises2) \
        and len(solutions1) == len(solutions2):
        for i in range(0, len(premises1)):
            if premises1[i] != premises2[i]:
                return False
        for i in range(0, len(solutions1)):
            if solutions1[i].conclusion.id != solutions2[i].conclusion.id \
                or cmp(solutions1[i].conclusion.description, solutions2[i].conclusion.description) > 0:
                return False
    return True


class TestDomainCBR:
    cbr: DomainCBR = None

    def retrieval_accuracy(self):
        for a_case in self.cbr.get_all_cases_list():
            retrieved_cases = self.cbr.retrieve_and_retain(a_case, 1.0)
            for sim_case in retrieved_cases:
                equal = True
                sim_premises = list(sim_case.case.problem.context.premises.values())
                a_premises = list(a_case.problem.context.premises.values())
                for i in range(0, len(a_premises)):
                    if sim_premises[i] != a_premises[i]:
                        equal = False
                assert equal

    def retrieval_consistency(self):
        all_cases = self.cbr.get_all_cases()
        all_cases2: List[List[DomainCase]] = []
        for cases_list in all_cases:
            all_cases2.append(cases_list)

        for cases_list in all_cases2:
            for a_case in cases_list:
                # Query the domainCBR for the list similarCases1
                similar_cases1 = self.cbr.retrieve_and_retain(a_case, 0.0)
                # Query again the domainCBR for the list of similarCases2
                similar_cases2 = self.cbr.retrieve_and_retain(a_case, 0.0)
                for case1 in similar_cases1:
                    found: bool = False
                    for case2 in similar_cases2:
                        if similar_domain_case_comparison(case1, case2):
                            assert True
                            found = True
                            break
                    if not found:
                        assert False

    def case_duplication(self):
        all_cases = self.cbr.get_all_cases()
        all_cases2: List[List[DomainCase]] = []
        for cases_list in all_cases:
            all_cases2.append(cases_list)

        for cases_list in all_cases2:
            for a_case in cases_list:
                similar_cases = self.cbr.retrieve_and_retain(a_case, 0.0)
                for i in range(len(similar_cases)):
                    case1 = similar_cases.pop(0)
                    assert case1 not in similar_cases

    def operating(self):
        first_case: DomainCase = self.cbr.get_all_cases_list()[0]
        similar_to_first_case = self.cbr.retrieve_and_retain(first_case, 0.0)
        assert similar_domain_case_comparison(similar_to_first_case[0],
                                              SimilarDomainCase(first_case, similar_to_first_case[0].similarity))

        premises: Dict[int, Premise] = {}
        for premise in first_case.problem.context.premises.values():
            premises[premise.id] = premise

        first_premise = list(premises.values())[0]
        first_premise.content += "aa"
        solutions = first_case.solutions
        justification = Justification("justification")
        dom_case = DomainCase(problem=Problem(
            context=DomainContext(premises=premises)), solutions=solutions, justification=justification)

        self.cbr.add_case(dom_case)

        similar_cases = self.cbr.retrieve_and_retain(dom_case, 0.0)
        assert similar_domain_case_comparison(similar_cases[0],
                                              SimilarDomainCase(dom_case, similar_cases[0].similarity))
        similar_to_first_case = self.cbr.retrieve_and_retain(first_case, 0.0)
        assert similar_domain_case_comparison(similar_to_first_case[0],
                                              SimilarDomainCase(first_case, similar_to_first_case[0].similarity))

    @pytest.fixture
    def domain_cbr_setup(self):
        file = os.path.abspath("tests/domain_cases_py.dat")
        self.cbr = DomainCBR(file, "/tmp/null", -1)

    def test_content(self, domain_cbr_setup):
        self.retrieval_accuracy()
        self.retrieval_consistency()
        self.case_duplication()  # This part is really slow
        self.operating()
