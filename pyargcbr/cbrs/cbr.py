from pickle import dump
from typing import Dict, List, Union, ValuesView, Sequence

from ..knowledge_resources.case import Case


def save_object(obj, file_name: str):
    """Saves an object in the file corresponding to the path; it's incremental.

    Args:
        obj (Object): The object that will be stored.
        file_name (str): The path to the file where the object will be stored.
    """
    with open(file_name, 'wb') as fh:
        dump(obj, fh)


class CBR:
    """Parent class for all the CBRs of the project"""
    case_base: Dict[Union[int, str], List[Case]]
    initial_file_path: str
    storing_file_path: str

    def __init__(self, initial_file_path: str, storing_file_path: str):
        """THE CBRs store cases that represent past experiences and their final outcome

        Args:
            initial_file_path (str): Path of the file where the initial cases base is stored
            storing_file_path (str): Path of the file where the cases base will be stored
        """
        self.initial_file_path = initial_file_path
        self.storing_file_path = storing_file_path

    def load_case_base(self):
        """Loads the case-base stored in the initial file path."""
        pass

    def add_case(self, new_case: Case) -> bool:
        """Adds a new case to case-base. Otherwise, if the same case exists in
        the case-base, adds the relevant data to the existing case. :param
        new_case: Thw case to be introduced :return: True if introduced,
        otherwise False

        Args:
            new_case (Case): The new case that will be added
        """
        pass

    def do_cache(self):
        """Stores the current domain-cases case-base to the storing file
        path.
        """
        with open(self.storing_file_path, "wb") as f:
            pass  # TODO This is supposed to reset the file    pending check
        self.do_cache_inc()

    def do_cache_inc(self):
        """Stores the current domain-cases case-base to the storing file path
        without removing the previous objects.
        """
        for a_case in self.get_all_cases():
            save_object(a_case, self.storing_file_path)

    def get_all_cases(self) -> ValuesView[Sequence[Case]]:
        """Returns all the cases from the cases base

        Returns:
            ValuesView[Sequence[Case]]: The list of cases
        """
        return self.case_base.values()

    def get_all_cases_list(self) -> Sequence[Case]:
        """Returns all the cases of the case-base

        Returns:
            Sequence[Case]: The list of cases
        """
        cases: List[Case] = []
        for list_cases in self.get_all_cases():
            cases += list_cases
        return cases
