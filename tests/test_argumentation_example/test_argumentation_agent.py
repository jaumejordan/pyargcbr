#!/usr/bin/env python

"""Test for the argumentation agents."""

import pytest


class TestForArgumentationAgents:
    """This class launches a test with argumentative agents, including the Commitment Store and a tester
    agent that acts as initiator

    """
    pass


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string
    assert True
