#!/usr/bin/env python

"""Test for the argumentation agents."""
from time import sleep
from typing import List

from loguru import logger
import pytest

from pyargcbr.agents.commitment_store_agent import CommitmentStore
from pyargcbr.knowledge_resources.domain_case import DomainCase
from pyargcbr.knowledge_resources.group import Group
from pyargcbr.knowledge_resources.valpref import ValPref
from tests.test_argumentation_example.agents.test_trigger_agent import TestTriggerAgent
from tests.test_argumentation_example.create_partitions import read_cases_file
from tests.test_argumentation_example.testable_argumentation_agents_creation import \
    create_empty_argument_cases_partitions, create_social_entities, create_friend_lists, create_dependency_relations, \
    create_and_launch_argumentation_agents


class TestForArgumentationAgents:
    """This class launches a test with argumentative agents, including the Commitment Store and a tester
    agent that acts as initiator

    """

    def __init__(self) -> None:
        super().__init__()
        self.n_operators = 7
        self.n_experts = 0
        self.n_managers = 0

        self.tester_agent_id = "testerAgent"
        self.finish_file_name = "test_argumentation_example/test_arg_agent_finished"
        self.initial_domain_file_names: List[str] = []
        self.initial_argument_file_names: List[str] = []
        self.test_domain_cases: List[DomainCase] =\
            read_cases_file("test_argumentation_example/resources/data/domain_cases/Helpdesk-DomainCases.json")
        for i in range(self.n_operators):
            self.initial_argument_file_names.append("resources/data/argument_cases/part_arg_inc/partArgOperator{}.dat"
                                                    .format(i))
        create_empty_argument_cases_partitions(self.initial_argument_file_names)

        self.social_entities = create_social_entities(base_name="ArgAgentTest", n_operators=self.n_operators,
                                                      n_experts=self.n_experts, n_managers=self.n_managers)
        self.friend_lists = create_friend_lists(self.social_entities)
        self.dependency_res_lists = create_dependency_relations(self.n_operators, self.n_experts, self.n_managers)

        self.values: List[str] = ["savings", "quality", "speed"]
        self.group = Group(id=0, name="group1", valpref=ValPref(self.values), agents=self.social_entities)

        self.cases = 45

        for i in range(self.n_operators):
            self.initial_domain_file_names.append("resources/data/domain_cases/partitions_inc/domCases{}"
                                                  "cas{}op.dat".format(self.cases,i))

        self.repetition = 0  # TODO: (Inherited from original code) put the correct init case

        self.dom_cases_vector = [self.test_domain_cases[self.repetition]]
        self.cs_id = "commitment_store@localhost"
        self.cs = CommitmentStore(self.cs_id, "secret")

        self.agents = create_and_launch_argumentation_agents(social_entities=self.social_entities,
                                                             friends_lists=self.friend_lists,
                                                             commitment_store_id=self.cs_id,
                                                             dependency_relations=self.dependency_res_lists,
                                                             group=self.group,
                                                             ini_domain_cases_file_path=self.initial_domain_file_names,
                                                             fin_domain_cases_file_path=self.initial_domain_file_names,
                                                             dom_cbr_index=0, dom_cbr_threshold=0.5,
                                                             ini_arg_cases_file_path=self.initial_argument_file_names,
                                                             fin_arg_cases_file_path=self.initial_argument_file_names)
        self.tester_agent = None

    @pytest.fixture
    def domain_cbr_setup(self):
        self.tester_agent = TestTriggerAgent(jid="testeragent@localhost", password="secret",
                                             social_entities=self.social_entities, commitment_store_id=self.cs_id,
                                             finish_filename=self.finish_file_name, domain_cases=self.dom_cases_vector,
                                             agents=self.agents)

    def test_argumentation(self, domain_cbr_setup):
        while True:
            sleep(1.5)
            try:
                with open(self.finish_file_name, "wr") as f:
                    content = f.read()
                    if content:
                        assert True
                        break
            except EOFError as e:
                logger.error(e)
                assert False
