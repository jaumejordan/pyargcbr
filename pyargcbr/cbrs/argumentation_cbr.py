from math import inf
from pickle import load
from typing import Dict, List, Sequence, Mapping, ValuesView

from loguru import logger

from ..agents.configuration import Configuration
from ..cbrs.cbr import CBR
from ..knowledge_resources.acceptability_status import AcceptabilityStatus
from ..knowledge_resources.argument_case import ArgumentCase
from ..knowledge_resources.argument_problem import ArgumentProblem
from ..knowledge_resources.position import Position
from ..knowledge_resources.premise import Premise
from ..knowledge_resources.similar_argument_case import SimilarArgumentCase
from ..knowledge_resources.social_context import SocialContext
from ..knowledge_resources.solution import Solution


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

    def load_case_base(self):
        """Loads the case-base stored in the initial file path"""
        super().load_case_base()  # Currently it does nothing
        self.case_base = {}
        introduced = 0
        not_introduced = 0
        str_ids: str = ""  # This was not on the original code ()
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
        logger.info(self.initial_file_path, "argument_cases: ", introduced + not_introduced,
                    "introduced: ", introduced, "not_introduced: ", not_introduced, "sols: ", str_ids)

    def add_case(self, new_arg_case: ArgumentCase) -> bool:
        """Two cases are equal if they have the same domain context, social
        context, conclusion and state of acceptability. If two cases are equal,
        also the domain-cases associated and attacks received must be added to
        the corresponding argument-case

        Args:
            new_arg_case (ArgumentCase): The new case that will (or not) be
                added
        """
        super().add_case(new_arg_case)  # Currently it does nothing
        new_case_premises: Dict[int, Premise] = new_arg_case.problem.context.premises
        # Copy the premises to an arraylist, ordered from lower to higher id
        new_case_premises_list: List[Premise] = list(new_case_premises.values())
        if len(new_case_premises_list) > 0:
            first_case_premise: Premise = new_case_premises_list[0]
            first_case_premise_id: int = first_case_premise.id
            candidate_cases: List[ArgumentCase] = self.case_base.get(first_case_premise_id, [])
            if candidate_cases:
                for arg_case in candidate_cases:
                    arg_case_premises = arg_case.problem.context.premises
                    # if the premises are the same with the same content, check
                    # if social context conclusion and state of acceptability
                    # are the same
                    if (self.is_same_domain_context_precise(new_case_premises_list, arg_case_premises)
                        and self.is_same_social_context(new_arg_case.problem.social_context,
                                                        arg_case.problem.social_context)
                        and new_arg_case.solutions.conclusion.id == arg_case.solutions.conclusion.id
                        and new_arg_case.solutions.acceptability_status == arg_case.solutions.acceptability_status):
                        # It is the same argument-case, so it is not introduced
                        # but we add associated cases and attacks received,
                        # and dialogue graphs and increase timesUsed

                        # Increase times used
                        arg_case.times_used += new_arg_case.times_used

                        # distinguishing premises
                        # Take care that distinguishing premises are NEVER translated to Dict
                        # (there are several dp with the same ID but different content in the List)
                        distinguishing_premises = arg_case.solutions.dist_premises
                        new_distinguishing_premises = new_arg_case.solutions.dist_premises
                        if not new_distinguishing_premises:  # it's a literal translation, maybe not necessary
                            new_distinguishing_premises = []
                        if not distinguishing_premises:
                            arg_case.solutions.dist_premises = new_distinguishing_premises
                        else:
                            arg_case.solutions.merge_distinguishing_premises(new_distinguishing_premises)

                        # exceptions
                        exceptions = arg_case.solutions.exceptions
                        new_exceptions = new_arg_case.solutions.exceptions
                        if not new_exceptions:
                            new_exceptions = []
                        if not exceptions:
                            arg_case.solutions.exceptions = new_exceptions
                        else:
                            arg_case.solutions.merge_exceptions(new_exceptions)

                        # presumptions
                        presumptions = arg_case.solutions.presumptions
                        new_presumptions = new_arg_case.solutions.presumptions
                        if not new_presumptions:
                            new_presumptions = []
                        if not presumptions:
                            arg_case.solutions.presumptions = new_presumptions
                        else:
                            arg_case.solutions.merge_presumptions(new_presumptions)

                        # counter examples domain case IDs
                        counter_examples_dom_case_ids = arg_case.solutions.counter_examples_dom_case_id
                        new_counter_examples_dom_case_ids = new_arg_case.solutions.counter_examples_dom_case_id
                        if not new_counter_examples_dom_case_ids:
                            new_counter_examples_dom_case_ids = []
                        if not counter_examples_dom_case_ids:
                            arg_case.solutions.counter_examples_dom_case_ids = new_counter_examples_dom_case_ids
                        else:
                            arg_case.solutions.merge_counter_examples_dom_cases_ids(new_counter_examples_dom_case_ids)

                        # counter examples argument case IDs
                        counter_examples_arg_case_ids = arg_case.solutions.counter_examples_arg_case_id
                        new_counter_examples_arg_case_ids = new_arg_case.solutions.counter_examples_arg_case_id
                        if not new_counter_examples_arg_case_ids:
                            new_counter_examples_arg_case_ids = []
                        if not counter_examples_arg_case_ids:
                            arg_case.solutions.counter_examples_arg_case_ids = new_counter_examples_arg_case_ids
                        else:
                            arg_case.solutions.merge_counter_examples_arg_cases_ids(new_counter_examples_arg_case_ids)

                            # associated domain cases
                            dom_cases_ids = arg_case.justification.domain_cases_ids
                            new_dom_cases_ids = new_arg_case.justification.domain_cases_ids
                            if not new_dom_cases_ids:
                                new_dom_cases_ids = []
                            if not dom_cases_ids:
                                arg_case.justification.dom_cases_ids = new_dom_cases_ids
                            else:
                                arg_case.justification.merge_domain_cases_ids(new_dom_cases_ids)

                            # associated argument cases
                            arg_cases_ids = arg_case.justification.argument_cases_ids
                            new_arg_cases_ids = new_arg_case.justification.argument_cases_ids
                            if not new_arg_cases_ids:
                                new_arg_cases_ids = []
                            if not arg_cases_ids:
                                arg_case.justification.arg_cases_ids = new_arg_cases_ids
                            else:
                                arg_case.justification.merge_argument_cases_ids(new_arg_cases_ids)

                            # dialogue graphs
                            dialogue_graphs = new_arg_case.justification.dialogue_graphs
                            graphs = arg_case.justification.dialogue_graphs
                            for diag in dialogue_graphs:
                                nodes_to_change = diag.get_nodes(new_arg_case.id)
                                if not nodes_to_change:
                                    logger.error("ERROR updating argument-case case-base.",
                                                 "No Argument-nodes matching in DialogueGraph")
                                    continue
                                for node in nodes_to_change:
                                    node.arg_case_id = arg_case.id
                                graphs.append(diag)

                        return False

            # the same case is not stored, so it is added
            if not candidate_cases:
                candidate_cases = []
            candidate_cases.append(new_arg_case)
            self.case_base[first_case_premise_id] = candidate_cases
            return True

        return False

    def get_degrees(self, arg_problem: ArgumentProblem, solution: Solution,
                    all_positions: Sequence[Position], index: int) -> List[float]:
        """Return a list with the degrees (attack, efficiency, explanatory
        power, persuasiveness, support and risk) of an argument-case

        Args:
            arg_problem (ArgumentProblem): Problem to solve
            solution (Solution): Solution that proposes the argument case
            all_positions (Sequence[Position]): Index of the position that
                represents the degrees which are been calculated
            index (int): Index of the position that represents the argument case
                which the degrees are been calculated

        Returns:
            List[float]: list with the degrees

        Raises:
            ValueError: When the index is bigger than the length of the
                all_positions list minus one
        """
        if index > len(all_positions) - 1 or index < 0:  # TODO rethink the return value, maybe we want to return 0.0s
            raise ValueError

        degrees: List[float] = []
        most_similar_arg_cases = self.get_most_similar_arg_cases(arg_problem)
        preserve: List[SimilarArgumentCase] = []
        for sim_arg in most_similar_arg_cases:
            # If it has different promote value, remove it
            if not sim_arg.case.solutions.value == solution.value:
                continue
            preserve.append(sim_arg)

        most_similar_arg_cases = preserve
        same_problem_accepted_arg_cases = ArgCBR.get_same_problem_accepted_arg_cases(most_similar_arg_cases)
        same_problem_conclusion_arg_cases = ArgCBR.get_same_problem_conclusion_arg_cases(most_similar_arg_cases,
                                                                                         solution)
        same_problem_conclusion_accepted_arg_cases = ArgCBR.get_same_problem_conclusion_accepted_arg_cases(
            same_problem_conclusion_arg_cases)
        same_problem_conclusion_accepted_attacked_arg_cases = \
            ArgCBR.get_same_problem_conclusion_accepted_attacked_arg_cases(same_problem_conclusion_accepted_arg_cases)

        arg_accepted_count = 0
        for arg_case in same_problem_conclusion_accepted_arg_cases:
            arg_accepted_count += arg_case.case.times_used

        arg_count = 0
        for arg_case in same_problem_conclusion_arg_cases:
            arg_count += arg_case.case.times_used

        persuasiveness_degree = 0.0
        if arg_count:
            persuasiveness_degree = arg_accepted_count / arg_count

        arg = 0
        for arg_case in most_similar_arg_cases:
            arg += arg_case.case.times_used

        support_degree = 0.0
        if arg:
            support_degree = arg_accepted_count / arg

        arg_accepted_count_attack = 0
        for arg_case in same_problem_conclusion_accepted_attacked_arg_cases:
            arg_accepted_count_attack += arg_case.case.times_used

        risk_degree = 0.0
        if arg_accepted_count_attack:
            risk_degrees = arg_accepted_count_attack / arg_accepted_count

        # Here we foster simplicity over efficiency, since for each position they are calculated
        # the attack, efficiency and power degrees of all_positions
        attack_degree = 0.0
        attack_degrees = ArgCBR.get_attack_degree(same_problem_accepted_arg_cases, all_positions)
        attack_degree = attack_degrees[index]
        efficiency_degree = 0.0
        efficiency_degrees = ArgCBR.get_efficiency_degree(same_problem_accepted_arg_cases, all_positions)
        efficiency_degree = efficiency_degrees[index]
        explanatory_power = 0.0
        explanatory_powers = ArgCBR.get_explanatory_power(same_problem_accepted_arg_cases, all_positions)
        explanatory_power = explanatory_powers[index]

        degrees.append(persuasiveness_degree)
        degrees.append(support_degree)
        degrees.append(risk_degree)
        degrees.append(attack_degree)
        degrees.append(efficiency_degree)
        degrees.append(explanatory_power)

        return degrees

    @staticmethod
    def get_same_problem_accepted_arg_cases(same_problem_arg_cases: List[SimilarArgumentCase]) -> \
        List[SimilarArgumentCase]:
        """Get similar argument cases to the given one with the same problem
        description and that were accepted in the past

        Args:
            same_problem_arg_cases (List[SimilarArgumentCase]): The argument
                cases with the same problem description

        Returns:
            List[SimilarArgumentCases]: Similar argument cases with the same
            problem description and that were accepted
        """
        return [i for i in same_problem_arg_cases
                if i.case.solutions.acceptability_status == AcceptabilityStatus.ACCEPTABLE]

    @staticmethod
    def get_same_problem_conclusion_arg_cases(same_problem_arg_cases: List[SimilarArgumentCase], solution: Solution) -> \
        List[SimilarArgumentCase]:
        """Get similar argument cases to the given one with the same problem
        description and conclusion

        Args:
            same_problem_arg_cases (List[SimilarArgumentCase]): Argument cases
                with the same problem description
            solution (Solution): The conclusion that must have the argument
                cases retrieved

        Returns:
            Similar argument cases with the same problem description and
            conclusion
        """
        return [i for i in same_problem_arg_cases if i.case.solutions.conclusion == solution.conclusion]

    @staticmethod
    def get_same_problem_conclusion_accepted_arg_cases(same_problem_conclusion_arg_cases: List[SimilarArgumentCase]) -> \
        List[SimilarArgumentCase]:
        """Get similar argument cases to the given one with the same problem
        description, conclusion and that were accepted in the past

        Args:
            same_problem_conclusion_arg_cases (List[SimilarArgumentCase]): Argument cases with the same problem
                description and conclusion

        Returns:
            Similar argument cases with the same problem description,
            conclusion, that were accepted
        """
        return [i for i in same_problem_conclusion_arg_cases
                if i.case.solutions.acceptability_status == AcceptabilityStatus.ACCEPTABLE]

    @staticmethod
    def get_same_problem_conclusion_accepted_attacked_arg_cases(
        same_problem_conclusion_accepted_attack_arg_cases: List[SimilarArgumentCase]) -> \
        List[SimilarArgumentCase]:
        """Get similar argument cases to the given one with the same problem
        description, and conclusion, that were accepted and that received
        attacks

        Args:
            same_problem_conclusion_accepted_attack_arg_cases: Argument cases
                with the same description, conclusion and that were accepted

        Returns:
            List[SimilarArgumentCase]: Similar argument cases with the same
            problem description, conclusion, that were accepted and that
            received attacks
        """
        return [i for i in same_problem_conclusion_accepted_attack_arg_cases
                if (len(i.case.solutions.counter_examples_dom_case_id) > 0
                    or len(i.case.solutions.counter_examples_arg_case_id) > 0
                    or len(i.case.solutions.dist_premises) > 0
                    or len(i.case.solutions.exceptions) > 0
                    or len(i.case.solutions.presumptions) > 0)]

    @staticmethod
    def get_all_position_arg_cases(same_problem_accepted_arg_cases: Sequence[SimilarArgumentCase],
                                   initial_positions: Sequence[Position]) -> List[List[SimilarArgumentCase]]:
        """Returns all the argument cases that have the same conclusion of the
        different given positions

        Args:
            same_problem_accepted_arg_cases: Argument cases with the same
                problem description and that were accepted
            initial_positions: Argument cases with different initial positions

        Returns:
            List[List[SimilarArgumentCase]]: Similar argument cases for each
            initial position
        """
        # Classify the argument cases, with the same problem description and that were
        # accepted, by its conclusion
        conclusion_sets: Dict[int, List[SimilarArgumentCase]] = {}
        for sim_arg_case in same_problem_accepted_arg_cases:
            conclusion_id = sim_arg_case.case.solutions.conclusion.id
            lst = conclusion_sets.get(conclusion_id, [])
            lst.append(sim_arg_case)
            conclusion_sets[conclusion_id] = lst
        # Put a list of argument cases for each initial position
        all_positions: List[List[SimilarArgumentCase]] = []
        for position in initial_positions:
            same_position = conclusion_sets.get(position.solution.conclusion.id, [])
            all_positions.append(same_position)
        return all_positions

    @staticmethod
    def get_attack_degree(same_problem_accepted_arg_cases: Sequence[SimilarArgumentCase],
                          initial_positions: Sequence[Position]) -> List[float]:
        """Returns the attack degree of each given Position

        Args:
            same_problem_accepted_arg_cases: Argument cases with the same
                problem description and that were accepted
            initial_positions: Different positions with the same problem
                description

        Returns:
            List[float]: The attack degrees of each initial position
        """
        all_position_cases = ArgCBR.get_all_position_arg_cases(same_problem_accepted_arg_cases, initial_positions)
        position_attacks_averages: List[float] = []
        min_attacks = inf
        max_attacks = -inf
        for arg_cases_list in all_position_cases:
            position_attacks_average = 0.0
            for sim_arg_case_position in arg_cases_list:
                n_attacks = len(sim_arg_case_position.case.solutions.counter_examples_dom_case_id) \
                            + len(sim_arg_case_position.case.solutions.dist_premises) \
                            + len(sim_arg_case_position.case.solutions.exceptions) \
                            + len(sim_arg_case_position.case.solutions.presumptions)
                if n_attacks < min_attacks:
                    min_attacks = n_attacks
                if n_attacks > max_attacks:
                    min_attacks = n_attacks
                position_attacks_average += n_attacks  # Add attacks to obtain the average
            # Calculate attacks average of this position and store it in the list
            position_attacks_average /= len(arg_cases_list)
            position_attacks_averages.append(position_attacks_average)

        attack_degrees: List[float] = []
        for n_attacks in position_attacks_averages:
            attack_degree = (n_attacks - min_attacks) / (max_attacks - min_attacks)
        return attack_degrees

    @staticmethod
    def get_efficiency_degree(same_problem_accepted_arg_cases: Sequence[SimilarArgumentCase],
                              initial_positions: Sequence[Position]) -> List[float]:
        """Returns the efficiency degree of each given initial position

        Args:
            same_problem_accepted_arg_cases: Argument cases with the same
                problem description and that were accepted
            initial_positions: Different positions with the same problem
                description

        Returns:
            List[float]: The efficiency degrees of each initial position
        """
        all_position_cases = ArgCBR.get_all_position_arg_cases(same_problem_accepted_arg_cases, initial_positions)
        position_attacks_averages: List[float] = []
        min_steps = inf
        max_steps = -inf
        for arg_cases_list in all_position_cases:
            position_steps_average = 0.0
            position_total_dialogue_graphs = 0
            for sim_arg_case_position in arg_cases_list:
                n_steps = 0
                for dialogue_graph in sim_arg_case_position.case.justification.dialogue_graphs:
                    dialogue_steps: int
                    try:
                        dialogue_steps = dialogue_graph.distance_to_final(sim_arg_case_position.case.id)
                    except (ValueError, TypeError) as e:
                        logger.exception(e)
                        continue
                    if dialogue_steps < min_steps:
                        min_steps = dialogue_steps
                    if dialogue_steps > max_steps:
                        max_steps = dialogue_steps

                    n_steps += dialogue_steps
                    position_total_dialogue_graphs += 1

                position_steps_average += n_steps  # Adds steps to obtain average

            # Calculate steps average of this position and store it in the list
            position_steps_average /= position_total_dialogue_graphs
            position_attacks_averages.append(position_steps_average)

        efficiency_degrees: List[float] = []
        for n_steps in position_attacks_averages:
            efficiency_degree = (n_steps - min_steps) / (max_steps - min_steps)
            efficiency_degrees.append(efficiency_degree)
        return efficiency_degrees

    @staticmethod
    def get_explanatory_power(same_problem_accepted_arg_cases: Sequence[SimilarArgumentCase],
                              initial_positions: Sequence[Position]) -> List[float]:
        """Returns the explanatory power of the given positions

        Args:
            same_problem_accepted_arg_cases: Argument cases with the same
                problem description and that were accepted
            initial_positions: Different positions with the same problem
                description

        Returns:
            List[float]: The explanatory power of each initial position
        """
        all_position_cases = ArgCBR.get_all_position_arg_cases(same_problem_accepted_arg_cases, initial_positions)
        kr_averages: List[float] = []
        # Calculate min and max number of used knlowledge resources
        min_kr = inf
        max_kr = -inf
        for arg_cases_list in all_position_cases:
            kr_average = 0.0
            for sim_arg_case_position in arg_cases_list:
                n_kr = len(sim_arg_case_position.case.justification.schemes) \
                       + len(sim_arg_case_position.case.justification.domain_cases_ids) \
                       + len(sim_arg_case_position.case.justification.argument_cases_ids)
                if n_kr < min_kr:
                    min_kr = n_kr
                if n_kr > max_kr:
                    max_kr = n_kr
                kr_average += n_kr  # Adds knowledge resources to the count to obtain the average

            # Calculate knowledge resources average of this position and store it in the list
            kr_average /= len(arg_cases_list)
            kr_averages.append(kr_average)

        explanatory_powers: List[float] = []
        for n_kr in kr_averages:
            explanatory_power = (n_kr - min_kr) / (max_kr - min_kr)
            explanatory_powers.append(explanatory_power)
        return explanatory_powers

    def get_same_domain_domain_and_social_context_accepted(self, premises: Mapping[int, Premise], solution: Solution,
                                                           social_context: SocialContext) -> List[SimilarArgumentCase]:
        """Returns the accepted argument cases with the same domain and social
        context that have been accepted in the past

        Args:
            premises (Mapping[int, Premise]: Premises that describe the domain context
            solution (Solution): Solution of the problem
            social_context (SocialContext): Social context of the current
                situation

        Returns:
            Argument cases with the same domain and social context that have
            been accepted
        """
        final_arg_cases: List[SimilarArgumentCase] = []
        c = Configuration()

        domain_similar_arg_cases = self.get_domain_similar_arg_cases(premises)
        for current_arg_case in domain_similar_arg_cases:
            suitability = 0.0
            if social_context.relation == current_arg_case.problem.social_context.relation:
                proponent_id_comp = 0.0
                proponent_pref_comp = 0.0
                opponent_id_comp = 0.0
                opponent_pref_comp = 0.0
                group_id_comp = 0.0
                group_pref_comp = 0.0
                if social_context.proponent.id == current_arg_case.problem.social_context.proponent.id:
                    proponent_id_comp = c.arg_cbr_proponent_id_weight
                if social_context.proponent.valpref.get_preferred() == \
                    current_arg_case.problem.social_context.proponent.valpref.get_preferred():
                    proponent_pref_comp = c.arg_cbr_proponent_pref_weight

                if social_context.opponent.id == current_arg_case.problem.social_context.opponent.id:
                    opponent_id_comp = c.arg_cbr_opponent_id_weight
                if social_context.opponent.valpref.get_preferred() == \
                    current_arg_case.problem.social_context.opponent.valpref.get_preferred():
                    opponent_pref_comp = c.arg_cbr_opponent_pref_weight

                if social_context.group.id == current_arg_case.problem.social_context.group.id:
                    group_id_comp = c.arg_cbr_group_id_weight
                if social_context.group.valpref.get_preferred() == \
                    current_arg_case.problem.social_context.group.valpref.get_preferred():
                    group_pref_comp = c.arg_cbr_group_pref_weight

                suitability = (proponent_id_comp + proponent_pref_comp + opponent_id_comp + opponent_pref_comp
                               + group_id_comp + group_pref_comp) / \
                              (c.arg_cbr_proponent_id_weight + c.arg_cbr_proponent_pref_weight +
                               c.arg_cbr_opponent_id_weight + c.arg_cbr_opponent_pref_weight +
                               c.arg_cbr_group_id_weight + c.arg_cbr_group_pref_weight)

                final_arg_cases.append(SimilarArgumentCase(current_arg_case, suitability))
        # Only with the same solution ID, and the same promoted value. Only accepted cases
        return [i for i in final_arg_cases if i.case.solutions.conclusion.id == solution
                and i.case.solutions.value == solution.value
                and i.case.solutions.acceptability_status == AcceptabilityStatus.ACCEPTABLE]

    def get_most_similar_arg_cases(self, arg_problem: ArgumentProblem) -> List[SimilarArgumentCase]:
        """Get the argument cases with the same domain context as the given
        argument case and the same dependency relation. The returned argument
        cases are weighted with a degree of suitability that depends on the
        degree of similarity with the social context of the given argument-case

        Args:
            arg_problem (ArgumentProblem): The argument problem with a specific
                domain context and social context that the returned
                argument-cases have to be similar

        Returns:
            Similar argument cases that have the same domain context as the
            given argument case and the same dependecy relation, weighted with a
            suitability degree
        """
        most_similar_arg_cases: List[SimilarArgumentCase] = []
        c = Configuration()

        domain_similar_arg_cases = self.get_domain_similar_arg_cases(arg_problem.context.premises)
        for current_arg_case in domain_similar_arg_cases:
            suitability = 0.0
            social_context = arg_problem.social_context
            if social_context:
                if (not social_context.relation or
                    social_context.relation == current_arg_case.problem.social_context.relation):
                    proponent_id_comp = 0.0
                    proponent_pref_comp = 0.0
                    opponent_id_comp = 0.0
                    opponent_pref_comp = 0.0
                    group_id_comp = 0.0
                    group_pref_comp = 0.0

                    if arg_problem.social_context.proponent.id == current_arg_case.problem.social_context.proponent.id:
                        proponent_id_comp = c.arg_cbr_proponent_id_weight
                    if arg_problem.social_context.proponent.valpref.get_preferred() == \
                        current_arg_case.problem.social_context.proponent.valpref.get_preferred():
                        proponent_pref_comp = c.arg_cbr_proponent_pref_weight

                    if arg_problem.social_context.opponent.id == current_arg_case.problem.social_context.opponent.id:
                        opponent_id_comp = c.arg_cbr_opponent_id_weight
                    if arg_problem.social_context.opponent.valpref.get_preferred() == \
                        current_arg_case.problem.social_context.opponent.valpref.get_preferred():
                        opponent_pref_comp = c.arg_cbr_opponent_pref_weight

                    if arg_problem.social_context.group.id == current_arg_case.problem.social_context.group.id:
                        group_id_comp = c.arg_cbr_group_id_weight
                    if arg_problem.social_context.group.valpref.get_preferred() == \
                        current_arg_case.problem.social_context.group.valpref.get_preferred():
                        group_pref_comp = c.arg_cbr_group_pref_weight

                    suitability = (proponent_id_comp + proponent_pref_comp + opponent_id_comp + opponent_pref_comp
                                   + group_id_comp + group_pref_comp) / \
                                  (c.arg_cbr_proponent_id_weight + c.arg_cbr_proponent_pref_weight +
                                   c.arg_cbr_opponent_id_weight + c.arg_cbr_opponent_pref_weight +
                                   c.arg_cbr_group_id_weight + c.arg_cbr_group_pref_weight)

            most_similar_arg_cases.append(SimilarArgumentCase(current_arg_case, suitability))
        return most_similar_arg_cases

    def get_domain_similar_arg_cases(self, desired_premises: Mapping[int, Premise]) -> List[ArgumentCase]:
        """Returns a list with argument cases with the same given premises (id
        and content) in the domain context

        Args:
            desired_premises: Dictionary with the desired premises

        Returns:
            Argument cases with the same given premises in the domain context
        """
        domain_similar_cases: List[ArgumentCase] = []
        # Copy the premises to a list (ordered from lower to higher id)
        desired_premises_list = list(desired_premises.values())

        # We obtain the cases by their lower ID because they are indexed by their lower ID
        # and we want to get cases that have the same domain case premises
        # So it is not neccesary to get the cases of the lists of other premises IDs
        if desired_premises_list:
            first_case_premise = desired_premises_list[0]
            first_premise_id = first_case_premise.id
            candidate_cases = self.case_base.get(first_premise_id, [])
            if candidate_cases:
                for arg_case in candidate_cases:
                    arg_case_premises = arg_case.problem.context.premises
                    # If the premises are the same with the same content. it is asimilar
                    # argument case. Add it to the final list
                    if self.is_same_domain_context(desired_premises_list, arg_case_premises):
                        domain_similar_cases.append(arg_case)
        return domain_similar_cases

    @staticmethod
    def is_same_domain_context(premises1: Sequence[Premise], premises2: Mapping[int, Premise]) -> bool:
        """Returns true if all the premises in the given List are the same (id
        and content)

        Args:
            premises1: (Sequence[Premise]): The given premises list
            premises2: (Mapping[int, Premise]): The given premises dict

        Returns:
            bool: True if it is the same domain context, otherwise False
        """
        for current_premise1 in premises1:
            current_premise2: Premise = premises2.get(current_premise1.id, None)
            # If a premise does not exist or the content is different, this case is not valid
            if (not current_premise2 or
                not current_premise2.content.lower() == current_premise1.content.lower()):
                return False
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
        else:
            return ArgCBR.is_same_domain_context(premises1, premises2)

    @staticmethod
    def is_same_social_context(social_context1: SocialContext, social_context2: SocialContext) -> bool:
        """Determines whether the given social contexts are the same (dependency
        relation, group, proponent and opponent) or not

        Args:
            social_context1 (SocialContext): A social context to be compared
            social_context2 (SocialContext): The social context to be compared
                with

        Returns:
            bool: True if the contexts are the same, False otherwise
        """
        # If used in the application domain, add list of proponents,
        # opponents and groups (checking that norms and valprefs are the same)
        if (social_context1.relation != social_context2.relation
            or social_context1.group.id != social_context2.group.id
            or social_context1.opponent.id != social_context2.opponent.id
            or social_context1.proponent.id != social_context2.proponent.id):
            return False
        return True

    def do_cache(self):
        super().do_cache()

    def do_cache_inc(self):
        super().do_cache_inc()

    def get_all_cases(self) -> ValuesView[Sequence[ArgumentCase]]:  # here we go again with annotations
        return super().get_all_cases()

    def get_all_cases_list(self) -> Sequence[ArgumentCase]:
        return super().get_all_cases_list()
