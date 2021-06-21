from typing import List, Tuple
from itertools import permutations

from pyargcbr.knowledge_resources.valpref import ValPref


class TestableArgumentationAgentsCreation:
    """This class has different methods to create groups of agents and some of their parameters

    """
    @staticmethod
    def get_valpref_list(values: Tuple[str] = ("savings", "quality", "speed")) -> List[ValPref]:
        """Gets a Tuple of str representing the values and returns a list of
        ValPref result of the permutation of these values

        Args:
            values (Tuple[str]): All the preferred values to be permuted. By
            default these are: ("savings", "quality", "speed")

        Returns:
            List[ValPref]: The resultant List of ValPref
        """
        value_permutations = permutations(values)
        preferred_values: List[ValPref] = [ValPref(values=list(perm)) for perm in value_permutations]
        return preferred_values

    @staticmethod
    def get_valpref_void_list() -> List[ValPref]:
        """Returns a List of ValPref with void preference

        Returns:
            List[ValPref]: The resultant List of ValPref with void preference
        """
        return TestableArgumentationAgentsCreation.get_valpref_list(values=tuple(""))
