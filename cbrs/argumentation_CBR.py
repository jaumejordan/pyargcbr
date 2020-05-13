from typing import Dict, List, Union, Sequence, Mapping

from cbrs.CBR import CBR
from pickle import load, dump

from knowledge_resources.argument_case import ArgumentCase
from knowledge_resources.case import Case
from knowledge_resources.premise import Premise
from knowledge_resources.social_context import SocialContext


class ArgCBR(CBR):
    """This class implements the argumentation CBR. This CBR stores
    argument-cases that represent past argumentation experiences and their final
    outcome.
    """

    def __init__(self, initial_file_path: str, storing_file_path: str):
        """
        Args:
            initial_file_path (str): The path of the file to load the initial
                domain-cases.
            storing_file_path (str): The path of the file where the final
                domain-cases will be stored.
        """
        super().__init__(initial_file_path, storing_file_path)
        self.load_case_base()

    def load_case_base(self, verbose: bool = False):
        """Loads the case-base stored in the initial file path

        Args:
            verbose (bool): If true prints a summary of th result after the
                execution
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
        """
        Args:
            new_arg_case (ArgumentCase):
        """
        super().add_case(new_arg_case)  # Currently it does nothing
        # Two cases are equal if they have the same domain context, social context,
        # conclusion and state of acceptability. If two cases are equal, also the domain-cases associated and attacks
        # received must be added to the corresponding argument-case
        new_case_premises: Dict[int, Premise] = new_arg_case.problem.context.premises
        # Copy the premises to an arraylist, ordered from lower to higher id
        new_case_premises_list: List[Premise] = list(new_case_premises.values())
        if len(new_case_premises_list) > 0:
            first_case_premise: Premise = new_case_premises_list[0]
            first_case_premise_id: int = first_case_premise.id
            candidate_cases: List[ArgumentCase] = self.case_base.get(first_case_premise_id) # Problems with Union[]
            if candidate_cases:
                for arg_case in candidate_cases:
                    arg_case_premises = arg_case.problem.context.premises
                    # if the premises are the same with the same content, check
                    # if social context conclusion and state of acceptability
                    # are the same

        return True

    @staticmethod
    def is_same_domain_context_precise(premises1: Sequence[Premise], premises2: Mapping[int, Premise]) -> bool:
        """Returns true if all the premises in the given List are the same (id
        and content) in the Dict and there are the same amount of them

        Args:
            premises1: (Sequence[Premise]): The given premises list
            premises2: (Mapping[int, Premise]): The given premises dict

        Returns:
            bool: True if it is the same domain context, otherwise False
        """
        if len(premises2) != len(premises1):
            return False
        for current_premise1 in premises1:
            current_premise2: Premise = premises2.get(current_premise1.id, None)
            # If a premise does not exist or the content is different, this case is not valid
            if (not current_premise2 or
                not current_premise2.content.lower() == current_premise1.content.lower()):
                return False
        return True

    @staticmethod
    def is_same_social_context(social_context1: SocialContext, social_context2: SocialContext) -> bool:
        """Determines whether the given social contexts are the same (dependency
        relation, group, proponent and opponent) or not

        Args:
            social_context1 (SocialContext): A social context to be compared
            social_context2 (SocialContext): The social context to be compared
                with

        Returns:

        """
        # If used in the application domain, add list of proponents,
        # opponents and groups (checking that norms and valprefs are the same)

