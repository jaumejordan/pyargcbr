from typing import Dict, List, Union

from cbrs.CBR import CBR
from pickle import load, dump

from knowledge_resources.argument_case import ArgumentCase
from knowledge_resources.case import Case
from knowledge_resources.premise import Premise


class argCBR(CBR):
    """
    This class implements the argumentation CBR. This CBR stores argument-cases
    that represent past argumentation experiences and their final outcome.

    Attributes:
         case_base (Dict[int, List[ArgumentCase]]): .
         initial_file_path (str): The path of the file to load the initial domain-cases.
         storing_file_path (str): The path of the file where the final domain-cases will be stored.
    """

    def __init__(self, initial_file_path: str, storing_file_path: str):
        super().__init__(initial_file_path, storing_file_path)
        self.load_case_base()

    def load_case_base(self, verbose: bool = False):
        """
        Loads the case-base stored in the initial file path.
        :param verbose: If true prints a summary of th result after the execution
        """
        super().load_case_base()  # Currently it does nothing
        self.case_base = {}
        introduced = 0
        not_introduced = 0
        str_ids:str = ""  # This was not on the original code ()
        with open(self.initial_file_path, 'rb') as fh:
            while True:
                try:
                    aux = load(fh)
                    if type(aux) == ArgumentCase:
                        a_case: ArgumentCase = aux
                        str_ids += str(a_case.solutions.conclusion.id) + " "
                        returned_value = self.add_case(a_case)
                        if returned_value:
                            introduced += 1
                        else:
                            not_introduced += 1
                except EOFError:
                    break
        if verbose:
            print(self.initial_file_path, "argument_cases: ", introduced + not_introduced,
                  "introduced: ", introduced, "not_introduced: ", not_introduced, "sols: ", str_ids)

    def add_case(self, new_arg_case: ArgumentCase) -> bool:
        super().add_case(new_arg_case)  # Currently it does nothing
        # Two cases are equal if they have the same domain context, social context,
        # conclusion and state of acceptability. If two cases are equal, also the domain-cases associated and attacks
        # received must be added to the corresponding argument-case
        new_case_premises = new_arg_case.problem.context.premises
        # Copy the premises to an arraylist, ordered from lower to higher id
        new_case_premises_list: List[Premise] = list(new_case_premises.values())
        if len(new_case_premises_list) > 0:
            first_case_premise = new_case_premises_list[0]
            first_case_premise_id = first_case_premise.id
            candidate_cases: List[ArgumentCase] = self.case_base.get(first_case_premise_id) # Problems with Union[]
            if candidate_cases:
                for arg_case in candidate_cases:
                    arg_case_premises = arg_case.problem.context.premises
                    # if the premises are the same with the same content, check
                    # if social context conclusion and state of acceptability
                    # sre the same

        return True



