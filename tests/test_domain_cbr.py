#!/usr/bin/env python

"""Tests for `pyargcbr` package."""

import pytest


from pyargcbr import pyargcbr
from knowledge_resources.domain_case import DomainCase
from knowledge_resources.domain_context import DomainContext
from knowledge_resources.justification import Justification
from knowledge_resources.premise import Premise
from knowledge_resources.problem import Problem
from knowledge_resources.similar_domain_case import SimilarDomainCase
from knowledge_resources.solution import Solution

from cbrs.domain_CBR import DomainCBR


class TestDomainCBR():
    cbr: DomainCBR = None

    def set_up(self):
        self.cbr = DomainCBR("domain_cases_py.dat", "tmp/null", -1)

    def retrieval_accuracy(self):
        for a_case in self.cbr.get_all_cases_list():
            retrieved_cases = self.cbr.retrieve_and_retain(a_case, 1.0)
            for sim_case in retrieved_cases:
                comp:bool = sim_case.caseb.problem.context.premises == a_case.problem.context.premises
                print(comp)
                assert comp # TODO is this a good way to compare two dicts?

    @pytest.fixture
    def response(self):
        pass

    def test_content(self, response):
        self.set_up()
        self.retrieval_accuracy()
