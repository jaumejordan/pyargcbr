#!/usr/bin/env python

"""Tests for `pyargcbr` package."""
import os
from typing import List

import pytest

from pyargcbr.cbrs.argumentation_cbr import ArgCBR
from pyargcbr.knowledge_resources.argument_case import ArgumentCase


class TestArgumentationCBR:
    cbr: ArgCBR = None

    def retrieval_accuracy(self):
        # For each ticket in arguments case base
        # Query the ArgCBR for the most similar case
        for a_case in self.cbr.get_all_cases_list():
            retrieved_cases = self.cbr.get_most_similar_arg_cases(a_case.problem)
            if retrieved_cases:
                sim_case = retrieved_cases[0]
                assert sim_case.case.id == a_case.id
            else:
                assert False

    def retrieval_consistency(self):
        all_cases = self.cbr.get_all_cases()
        all_cases2: List[List[ArgumentCase]] = []
        for cases_list in all_cases:
            all_cases2.append(cases_list)

        for cases_list in all_cases2:
            for a_case in cases_list:
                # Query the domainCBR for the list similarCases1
                similar_cases1 = self.cbr.get_most_similar_arg_cases(a_case.problem)
                # Query again the domainCBR for the list of similarCases2
                similar_cases2 = self.cbr.get_most_similar_arg_cases(a_case.problem)
                for case1 in similar_cases1:
                    found: bool = False
                    # Retrieve case2 from similar_cases2 shuch that case1 == case2
                    for case2 in similar_cases2:
                        if case1.similarity == case2.similarity \
                            and case1.case.id == case2.case.id:
                            assert True
                            found = True
                            break
                    if not found:
                        assert False

    def case_duplication(self):
        all_cases = self.cbr.get_all_cases()
        all_cases2: List[List[ArgumentCase]] = []
        for cases_list in all_cases:
            all_cases2.append(cases_list)

        for cases_list in all_cases2:
            for a_case in cases_list:
                similar_cases = self.cbr.get_most_similar_arg_cases(a_case.problem)
                for i in range(len(similar_cases)):
                    case1 = similar_cases.pop(0)
                    assert case1 not in similar_cases

    @pytest.fixture
    def arg_cbr_setup(self):
        file = os.path.abspath("tests/argument_cases_py.dat")
        self.cbr = ArgCBR(file, "/tmp/null")

    def test_content(self, arg_cbr_setup):
        # self.retrieval_accuracy()   # TODO check
        self.retrieval_consistency()
        self.case_duplication()
