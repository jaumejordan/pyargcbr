from typing import List, Dict, Optional, Any, Mapping, Union
from datetime import datetime

from loguru import logger
from spade.agent import Agent
from spade.behaviour import FSMBehaviour
from spade.message import Message

from agents.arg_message import ArgMessage
from agents.protocol import ADD_ARGUMENT_PERF, REMOVE_ARGUMENT_PERF, ADD_POSITION_PERF, ATTACK_PERF, ADD_POSITION_PERF, \
    GET_POSITION_PERF, GET_ALL_POSITIONS_PERF, NO_COMMIT_PERF, ASSERT_PERF, ATTACK_PERF, ADD_DIALOGUE_PERF, \
    GET_DIALOGUE_PERF, ENTER_DIALOGUE_PERF, WITHDRAW_DIALOGUE_PERF, DIE_PERF, REGISTER_PROTOCOL, REQUEST_PROTOCOL, \
    ACCEPT_PERF, REQUEST_PERF, LAST_MODIFICATION_DATE_PERF, PROTOCOL, PERFORMATIVE, CONVERSATION, MessageCodification, \
    WHY_PERF, NOTHING_PERF
from cbrs.argumentation_cbr import ArgCBR
from cbrs.domain_cbr import DomainCBR
from knowledge_resources.argument import Argument
from knowledge_resources.argument_case import ArgumentCase
from knowledge_resources.argument_justification import ArgumentJustification
from knowledge_resources.argument_problem import ArgumentProblem
from knowledge_resources.argument_solution import ArgumentSolution
from knowledge_resources.argumentation_scheme import ArgumentationScheme
from knowledge_resources.dialogue_graph import DialogueGraph
from knowledge_resources.domain_case import DomainCase
from knowledge_resources.domain_context import DomainContext
from knowledge_resources.group import Group
from knowledge_resources.position import Position
from knowledge_resources.premise import Premise
from knowledge_resources.problem import Problem
from knowledge_resources.similar_argument_case import SimilarArgumentCase
from knowledge_resources.similar_domain_case import SimilarDomainCase
from knowledge_resources.social_context import DependencyRelation, SocialContext
from knowledge_resources.social_entity import SocialEntity
from knowledge_resources.solution import Solution
from knowledge_resources.support_set import SupportSet

DATE_FORMAT = "%m/%d/%Y, %H:%M:%S"


class ArgAgent(Agent):
    """This class implements the argumentative agent as a CAgent. It can engage in an
    argumentation dialogue to solve a problem.
    The agent can follow different argumentation tactics by setting different values for the weights
    of the support factor (SF):
    - Persuasive tactic: wPD = 1; rest of weights = 0
    - Maximise-support tactic: wSD = 1; rest of weights = 0
    - Minimise-risk tactic: wRD = 1; rest of weights = 0
    - Minimise-attack tactic: wAD = 1; rest of weights = 0
    - Maximise-efficiency tactic: wED = 1; rest of weights = 0
    - Explanatory tactic: wEP = 1; rest of weights = 0
    """

    def __init__(self, jid: str, password: str, my_social_entity: SocialEntity, my_friends: List[SocialEntity],
                 dependency_relations: List[DependencyRelation], group: Group, commitment_store_id: str,
                 tester_agent_id: str, ini_domain_cases_file_path: str, fin_domain_cases_file_path: str,
                 dom_cbr_index: int, dom_cbr_threshold: float, ini_arg_cases_file_path: str,
                 fin_arg_cases_file_path: str, wpd: float, wsd: float, wrd: float, wad: float, wed: float, wep: float):
        """Main method to build Argumentative Agents

        Args:
            (str): jid used to identify the agent (spade)
            password (str): password of the agent (spade)
            my_social_entity (SocialEntity): Social entity of the agent
            my_friends (List[SocialEntity): List with the social entities that represent the agent's friend
            dependency_relations (List[DependencyRelation]): List with the dependency relations
            of the agent with its friends
            group Group: The group the agent belongs to
            commitment_store_id (str): ID of the commitment store
            tester_agent_id (str): TODO ID of the tester agent to run tests in the system
            ini_domain_cases_file_path (str): File with the original domain cases case base
            fin_domain_cases_file_path (str): File to write the updated domain cases case base
            dom_cbr_index (int):
            dom_cbr_threshold (float):
            ini_arg_cases_file_path (str): File with the original argument cases case base
            fin_arg_cases_file_path (str): File with the updated argument cases case base
            wpd (float): Weight of the Persuasion Degree
            wsd (float): Weight of the Support Degree
            wrd (float): Weight of the Risk Degree
            wad (float): Weight of the Attack Degree
            wed (float): Weight of the Efficiency Degree
            wep (float): Weight of the Explanatory Power
        """
        super().__init__(jid, password)
        self.my_id: str = jid
        self.prefered_values: List[str] = my_social_entity.valpref.values
        self.my_social_entity: SocialEntity = my_social_entity
        self.my_friends: List[SocialEntity] = my_friends
        self.dependency_relations: List[DependencyRelation] = dependency_relations
        self.my_group: Group = group
        self.commitment_store_id: str = commitment_store_id

        self.domain_cbr: DomainCBR = DomainCBR(ini_domain_cases_file_path, fin_domain_cases_file_path, dom_cbr_index)
        self.arg_cbr: ArgCBR = ArgCBR(ini_arg_cases_file_path, fin_arg_cases_file_path)
        self.domain_cbr_threshold: float = dom_cbr_threshold
        self.similar_domain_cases: Optional[List[SimilarDomainCase]] = None

        self.w_similarity: Optional[float] = None
        self.w_arg_suit_factor: Optional[float] = None

        self.wpd: float = wpd
        self.wsd: float = wsd
        self.wrd: float = wrd
        self.wad: float = wad
        self.wed: float = wed
        self.wep: float = wep

        self.current_dialogue_id: Optional[str] = None
        self.current_problem: Optional[Problem] = None
        self.current_dom_case_to_solve: Optional[DomainCase] = None
        self.current_position: Optional[Position] = None
        self.last_position_before_none: Optional[Position] = None
        self.dialogue_graphs: Dict[str, List[DialogueGraph]] = {}
        self.current_dialogue_graph: Optional[DialogueGraph] = None

        self.sub_dialogue_agent_id: str = ""
        self.different_positions: List[Position]

        self.dialogue_time: float = 0.0
        self.current_pos_accepted: int = 0
        self.agreement_reached: int = 0
        self.acceptance_frequency: int = 0
        self.cotes_received: int = 0
        self.used_arg_cases: int = 0
        self.alive: bool = True

        self.my_positions: Optional[List[Position]] = None
        self.positions_generated: bool = False
        self.asked_positions: List[Position] = []
        self.attended_why_petitions: Dict[str, List[Position]] = {}
        self.my_support_argument: Dict[str, List[Argument]] = {}
        self.my_used_locutions: int = 0  # TODO locutions or performatives

        self.my_used_support_arguments: Dict[str, List[Argument]] = {}
        self.my_used_attack_arguments: Dict[str, List[Argument]] = {}

        self.store_arguments: Dict[str, List[Argument]] = {}

    async def setup(self):  # TODO
        pass

    def finalize(self):  # TODO
        pass

    def enter_dialogue(self, dom_case: DomainCase, dialogue_id: str) -> ArgMessage:
        """Evaluates if the agent can enter in the dialogue offering a solution. If
        it can, it returns an message with the performative ENTER_DIALOGUE_PERF.
        If not, it returns the message with the performative WITHDRAW_DIALOGUE_PERF

        Args:
            dom_case (DomainCase): Domain case that represents the problem to solve
            dialogue_id (str): The dialogue identifier

        Returns:
            ArgMessage: A message with the corresponding performative
        """
        self.current_dom_case_to_solve = dom_case
        # Each agent adds domain cases with the agreed solution at the end of the dialogue

        # A test agent will give the initiator agent the problem to solve
        self.similar_domain_cases = self.domain_cbr.retrieve(dom_case.problem.context.premises,
                                                             self.domain_cbr_threshold)
        if self.similar_domain_cases:
            self.current_problem = Problem(DomainContext(dom_case.problem.context.premises))

            c_pos = self.current_position
            if c_pos:
                self.last_position_before_none = Position(c_pos.agent_id, c_pos.dialogue_id, c_pos.solution,
                                                          c_pos.premises, c_pos.domain_cases,
                                                          c_pos.domain_case_similarity)
            self.current_position = None
            self.positions_generated = False

            self.asked_positions: List[Position] = []
            self.attended_why_petitions: Dict[str, List[Position]] = {}
            self.store_arguments: Dict[str, List[Argument]] = {}
            self.dialogue_graphs: Dict[str, List[DialogueGraph]] = {}

            # Enter dialogue, add in commitment store
            return self.enter_dialogue_cs(dialogue_id)
        else:
            # not enter the dialogue
            return self.withdraw_dialogue()

    def withdraw_dialogue(self) -> ArgMessage:
        """Returns a message with the locution WITHDRAW_DIALOGUE_PERF

        Returns:
            ArgMessage: The message to be sent
        """
        c_pos = self.current_position
        if c_pos:
            self.last_position_before_none = Position(c_pos.agent_id, c_pos.dialogue_id, c_pos.solution,
                                                      c_pos.premises, c_pos.domain_cases,
                                                      c_pos.domain_case_similarity)
            self.current_position = None
            self.current_problem = None
            self.positions_generated = False

            self.my_used_locutions += 1
            return self.create_message(self.commitment_store_id, WITHDRAW_DIALOGUE_PERF, self.current_dialogue_id, None)

    def propose(self, pos: Position, dialogue_id: str) -> ArgMessage:
        """Returns a message with the performative ADD_POSITION_PERF and the position proposed

        Args:
            pos (Position): Position to propose
            dialogue_id (str): The dialogue identifier

        Returns:
            ArgMessage: The message to be sent
        """
        return self.add_position(pos, dialogue_id)

    def why(self, agent_id: str, pos: Position) -> ArgMessage:
        """Returns a message with the performative WHY to challenge the given position

        Args:
            agent_id (str): Agent identifier to ask it WHY is defending a position
            pos (Position): Position of the agent to ask WHY

        Returns:
            ArgMessage: The message to be sent
        """
        self.my_used_locutions += 1
        return self.create_message(agent_id, WHY_PERF, self.current_dialogue_id, pos)

    def no_commit(self, agent_id: str, pos: Position) -> ArgMessage:
        """Returns a message with the performative NO_COMMIT_PERF to challenge the given position

        Args:
            agent_id (str): Agent identifier to tell NO_COMMIT
            pos (Position): Position that the agent does NO_COMMIT TODO it seems like it's not used... weird

        Returns:
            ArgMessage: The message to be sent
        """
        self.my_used_locutions += 1
        c_pos = self.current_position
        if c_pos:
            self.last_position_before_none = Position(c_pos.agent_id, c_pos.dialogue_id, c_pos.solution,
                                                      c_pos.premises, c_pos.domain_cases,
                                                      c_pos.domain_case_similarity)
        self.current_position = None
        self.current_pos_accepted = 0
        # (the no commit is received also by the Commitment Store)
        return self.create_message(agent_id, NO_COMMIT_PERF, self.current_dialogue_id, None)

    def asserts(self, agent_id: str, arg: Argument) -> ArgMessage:
        """Returns a message with the performative ASSERT_PERF to challenge the given position

        Args:
            agent_id (str): Agent identifier to tell that this agent makes an ASSERT to respond its why
            arg (Argument): Asserted argument that the agent uses

        Returns:
            ArgMessage: The message to be sent
        """
        self.my_used_locutions += 1
        return self.create_message(agent_id, ASSERT_PERF, self.current_dialogue_id, arg)

    def accept(self, agent_id: str) -> ArgMessage:
        """Returns a message with the performative ACCEPT_PERF

        Args:
            agent_id: Agent identifier to tell that this agent makes an ACCEPT of its position or argument

        Returns:
            ArgMessage: The message to be sent
        """
        # Send it to the other agent
        self.my_used_locutions += 1
        return self.create_message(agent_id, ACCEPT_PERF, self.current_dialogue_id, None)

    def attack(self, agent_id: str, arg: Argument) -> ArgMessage:
        """Returns a message with the performative ATTACK_PERF and an attack argument

        Args:
            agent_id (str): Agent identifier to tell that this agent makes an ATTACK to its position or argument
            arg (Argument): Attack argument

        Returns:
            ArgMessage: The message to be sent
        """
        self.my_used_locutions += 1
        return self.create_message(agent_id, ATTACK_PERF, self.current_dialogue_id, arg)

    def nothing_msg(self) -> ArgMessage:
        """Returns a message with the performative NOTHING_PERF to send to any agent

        Returns:
            ArgMessage: The message to be sent
        """  # TODO a way to properly the "noOne" identifier part
        return self.create_message("noOne", NOTHING_PERF, self.current_dialogue_id, None)

    def get_my_last_used_argument(self, agent_id: str, arg_id: int) -> Optional[Argument]:
        """Returns the last used argument with another specified agent and with the given id

        Args:
            agent_id (str): Agent identifier that received the argument
            arg_id (int): Argument identifier

        Returns:
            Argument: The last used argument
        """
        attack_args = self.my_used_attack_arguments.get(agent_id, [])
        for arg in attack_args:
            if arg_id == arg.id:
                return arg

        support_args = self.my_used_support_arguments.get(agent_id, [])
        for arg in support_args:
            if arg_id == arg.id:
                return arg
        return None

    def generate_positions(self, prob: Problem) -> List[Position]:
        """Returns a list of positions with all generated positions to solve the specified problem, ordered
        from more to less suitability degree to the problem

        Args:
            prob (Problem): The problem to solve

        Returns:
            List[Position]: List with all generated positions
        """
        # The agent will always get the first position, removing it from its list of generated positions
        # When it has run out of positions, it has to withdraw from the dialogue

        # Generate all positions and store them in a list, ordered by Promoted
        # Value, and then, by Suitability = w*sim_degree + w2*suit_factor

        # At first we need make a query to DomainCBR to generate the possible solutions
        # Then, with each solution, create a Position
        # With each position, query the ArgCBR calculating the support factor for each position
        final_positions: List[Position] = []
        if not self.similar_domain_cases:
            logger.info("\n{}: NO similar domain cases\n", self.name)
        # similar_domain_cases has been initialized in enter_dialogue_cs, with the similar domain-cases to the problem
        else:
            # create a list of positions in each list of positions will be stored the positions with the same
            # Promoted Values
            positions_lists: List[List[Position]] = [[] for i in range(len(self.prefered_values))]

            for similar_domain_case in self.similar_domain_cases:
                case_solutions = similar_domain_case.case.solutions
                for solution in case_solutions:
                    index = self.get_preferred_value_index(solution.value)
                    # if the Promoted Value is one of the preferred values of the agent, the position is added.
                    # Otherwise it is not added
                    if index > -1:
                        support_domain_cases: List[DomainCase] = [similar_domain_case.case]

                        for similar_domain_case2 in self.similar_domain_cases:
                            for solution2 in similar_domain_case2.case.solutions:
                                if (solution2.conclusion.id == solution.conclusion.id
                                    and solution2.value == solution.value):
                                    support_domain_cases.append(similar_domain_case2)
                                    similar_domain_case2.case.remove_solution(solution2)

                                    if not similar_domain_case2.case.solutions:
                                        self.similar_domain_cases.remove(similar_domain_case2)
                                    break
                        pos = Position(self.my_id, self.current_dialogue_id, solution,
                                       similar_domain_case.case.problem.context.premises, support_domain_cases,
                                       similar_domain_case.similarity)

            # store all positions in a list, to calculate the attack degree, efficiency degree and explanatory power
            all_positions: List[Position] = [pos for positions_list in positions_lists for pos in positions_list]
            for positions_list in positions_lists:
                for position in positions_list:
                    social_context = SocialContext(proponent=self.my_social_entity, opponent=None,
                                                   group=self.my_group, relation=None)
                    argument_problem = ArgumentProblem(DomainContext(position.premises), social_context)

                    degrees = self.arg_cbr.get_degrees(argument_problem, position.solution, all_positions,
                                                       all_positions.index(position))
                    persuasiveness_degree = degrees[0]
                    support_degree = degrees[1]
                    risk_degree = degrees[2]
                    attack_degree = degrees[3]
                    efficiency_degree = degrees[40]
                    explanatory_power = degrees[5]
                    # SF =( (wPD * PD + wSD * SD + wRD * (1 - RD) + wAD * (1 - AD) + wED * ED + wEP * EP) ) / 6
                    arg_suitability_factor = (self.wpd * persuasiveness_degree + self.wsd * support_degree + self.wrd
                                              * (1 - risk_degree) + self.wad * (
                                                  1 - attack_degree) + self.wed * efficiency_degree
                                              + self.wed * explanatory_power)
                    position.arg_suitability_factor = arg_suitability_factor

                    # Assign weights in accordance with the quantity of knowledge of each type
                    domain_cases_num = len(self.similar_domain_cases)
                    argument_cases_num = len(self.arg_cbr.get_same_domain_domain_and_social_context_accepted(
                        position.premises, position.solution, social_context))
                    total_cases = domain_cases_num + argument_cases_num
                    if total_cases:
                        self.w_similarity = domain_cases_num / total_cases
                        self.w_arg_suit_factor = argument_cases_num / total_cases
                    else:
                        self.w_similarity = 0.5
                        self.w_arg_suit_factor = 0.5
                    final_suitability = position.domain_case_similarity * self.w_similarity + arg_suitability_factor * \
                                        self.w_arg_suit_factor
                    position.final_suitability = final_suitability

                positions_list = sorted(positions_list)
                final_positions.append(positions_list)

        solutions_str = ""
        for position in final_positions:
            solutions_str += str(position.solution.conclusion.id) + " "
        logger.info("\n{}. {} initial positions. ** Solutions: {}\n".format(self.name, len(final_positions),
                                                                            solutions_str))
        self.positions_generated = True
        return final_positions

    def generate_support_arguments(self, my_pos: Position, agent_id: str) -> List[Argument]:
        """Returns a list of support arguments for the given positions against the given agent

        Args:
            my_pos (Position): position to generate support arguments for
            agent_id: agent identifier to give support arguments to use against

        Returns:
            List[Argument]: List of support arguments
        """
        # First, assign weights in accordance with the quantity of knowledge
        final_support_arguments: List[Argument] = []
        friend_index = self.get_friend_index(agent_id)

        if friend_index < 0:
            pass  # TODO can this situation happen?
        opponent = self.my_friends[friend_index]
        relation = self.dependency_relations[friend_index]
        # Try to generate a support argument of the type:
        # 1) Argument Cases 2) Domain Cases 3) Premises

        social_context = SocialContext(self.my_social_entity, opponent, self.my_group, relation)
        # Create argument case with the domain case
        argument_problem = ArgumentProblem(DomainContext(self.current_position.premises), social_context)
        argument_solution = ArgumentSolution(conclusion=self.current_position.solution.conclusion,
                                             value=self.current_position.solution.value,
                                             times_used=self.current_position.solution.times_used)
        argument_justification = ArgumentJustification()
        argument_justification.domain_cases_ids = [domain_case.id for domain_case in self.current_position.domain_cases]

        argument_case_from_domain_case = ArgumentCase(arg_id=datetime.now().microsecond,
                                                      creation_date=datetime.now().strftime(DATE_FORMAT),
                                                      problem=argument_problem,
                                                      justification=argument_justification,
                                                      solution=argument_solution)
        # Create argument case with just the premises
        argument_justification_premises = ArgumentJustification()
        argument_case_premises = ArgumentCase(arg_id=datetime.now().microsecond,
                                              creation_date=datetime.now().strftime(DATE_FORMAT),
                                              problem=argument_problem,
                                              justification=argument_justification_premises,  # Here is the difference
                                              solution=argument_solution)
        # Extract argument cases
        argument_cases = self.arg_cbr.get_same_domain_domain_and_social_context_accepted(my_pos.premises,
                                                                                         my_pos.solution,
                                                                                         social_context)
        self.used_arg_cases += len(argument_cases)

        # Add an argument case with the domain case and the argument case with just the premises
        argument_cases.append(SimilarArgumentCase(argument_case_from_domain_case, 1))
        argument_cases.append(SimilarArgumentCase(argument_case_premises, 1))

        # This list contains positions that represent the different argument-cases
        # extracted just to calculate the degrees with the function get_degrees()
        all_positions: List[Position] = []
        for similar_argument_case in argument_cases:
            solution = Solution(similar_argument_case.case.solutions.conclusion,
                                similar_argument_case.case.solutions.value,
                                similar_argument_case.case.solutions.times_used)
            all_positions.append(Position(agent_id="", dialogue_id="", solution=solution,
                                          premises=similar_argument_case.case.problem.context.premises,
                                          domain_cases=None, domain_case_similarity=1.0))
        for similar_argument_case in argument_cases:
            solution = Solution(similar_argument_case.case.solutions.conclusion,
                                similar_argument_case.case.solutions.value,
                                similar_argument_case.case.solutions.times_used)
            degrees_list = self.arg_cbr.get_degrees(arg_problem=similar_argument_case.case.problem,
                                                    solution=solution, all_positions=all_positions,
                                                    index=argument_cases.index(similar_argument_case))
            persuasiveness_degree = degrees_list[0]
            support_degree = degrees_list[1]
            risk_degree = degrees_list[2]
            attack_degree = degrees_list[3]
            efficiency_degree = degrees_list[4]
            explanatory_power = degrees_list[5]
            # SF =( (wPD * PD + wSD * SD + wRD * (1 - RD) + wAD * (1 - AD) + wED * ED + wEP * EP) ) / 6
            arg_suitability_factor = (self.wpd * persuasiveness_degree + self.wsd * support_degree + self.wrd
                                      * (1 - risk_degree) + self.wad * (
                                          1 - attack_degree) + self.wed * efficiency_degree
                                      + self.wed * explanatory_power)
            # Assign weights in accordance with the quantity of knowledge of each type
            domain_cases_num = len(self.similar_domain_cases)
            argument_cases_num = len(self.arg_cbr.get_same_domain_domain_and_social_context_accepted(
                my_pos.premises, my_pos.solution, social_context))
            total_cases = domain_cases_num + argument_cases_num
            if total_cases:
                self.w_similarity = domain_cases_num / total_cases
                self.w_arg_suit_factor = argument_cases_num / total_cases
            else:
                self.w_similarity = 0.5
                self.w_arg_suit_factor = 0.5
            # Calculate suitability degree: with the current similarity in similar_argument_case,
            # and the suitability obtained from the ArgumentationCBR
            similar_argument_case.similarity = arg_suitability_factor * self.w_arg_suit_factor + \
                                               similar_argument_case.similarity * self.w_similarity

        argument_cases = sorted(argument_cases)
        premises = [premise for premise in my_pos.premises.values()]
        domain_cases_aux: List[DomainCase] = []
        argument_cases_aux: List[ArgumentCase] = []
        schemes: List[ArgumentationScheme] = []
        dist_premises: List[Premise] = []
        presumptions: List[Premise] = []
        exceptions: List[Premise] = []
        counter_examples_domain_cases: List[DomainCase] = []
        counter_examples_argument_cases: List[ArgumentCase] = []

        # Create a support argument with premises or domain cases, not directly with argument cases
        for i in range(len(argument_cases)):
            best_argument_case = argument_cases[i].case
            if best_argument_case:
                argument_cases_aux = []
                domain_cases_aux = []

                argument_justification2 = best_argument_case.justification
                domain_cases_justification = argument_justification2.domain_cases_ids
                argument_cases_justification = argument_justification2.argument_cases_ids
                argument_schemes_justification = argument_justification2.schemes
                dialogue_graphs_justification = argument_justification2.dialogue_graphs

                # Detect if it is the domain case justification argument
                if domain_cases_justification:
                    # Add the domain-case that justifies the position, since it is this argument:
                    # argument_case_from_domain_case
                    domain_cases_aux = self.current_position.domain_cases
                # if not, detect if it is the only premises justification argument
                elif (not argument_schemes_justification and not dialogue_graphs_justification
                      and not domain_cases_justification and not argument_cases_justification):
                    # Premises already in the premises list, do not add as a new argument-case
                    pass
                else:
                    argument_cases_aux.append(best_argument_case)
            support_set = SupportSet(premises, domain_cases_aux, argument_cases_aux, schemes, dist_premises,
                                     presumptions, exceptions, counter_examples_domain_cases,
                                     counter_examples_argument_cases)
            argument = Argument(datetime.now().microsecond, my_pos.solution.conclusion, my_pos.solution.times_used,
                                my_pos.solution.value, support_set, relation)
            final_support_arguments.append(argument)

        return final_support_arguments

    def generate_attack_argument(self, inc_argument: Argument, agent_id: str) -> Optional[Argument]:
        """Returns a n attack argument against the given argument of the the given agent

        Args:
            inc_argument (Argument): Previous argument of the agent to give an attack against
            agent_id: Agent identifier of the agent to attack

        Returns:
            Argument: List of support arguments
        """
        # Try to generate an attack argument:
        # Distinguishing premise or Counter-Example, depending on the attack received
        friend_index = self.get_friend_index(agent_id)
        if friend_index < 0:
            pass  # TODO can this situation happen?
        opponent = self.my_friends[friend_index]
        relation = self.dependency_relations[friend_index]
        # If the opponent is more powerful than me, do not attack
        if inc_argument.proponent_depen_relation < relation:
            return None

        social_context = SocialContext(self.my_social_entity, opponent, self.my_group, relation)
        # Extract argument-cases that match my position
        my_pos_premises = self.current_position.premises
        sol = self.current_position.solution
        arg_cases = self.arg_cbr.get_same_domain_domain_and_social_context_accepted(my_pos_premises, sol,
                                                                                    social_context)
        self.used_arg_cases += len(arg_cases)
        # Create argument cases with the domain cases
        for i in range(len(self.current_position.domain_cases)):
            argument_problem = ArgumentProblem(DomainContext(self.current_position.domain_cases[i].problem.context. \
                                                             premises), social_context)
            argument_solution = ArgumentSolution(conclusion=self.current_position.solution.conclusion,
                                                 value=self.current_position.solution.value,
                                                 times_used=self.current_position.solution.times_used)
            argument_justification = ArgumentJustification()
            argument_justification.add_domain_case(self.current_position.domain_cases[i].id)

            arg_case_from_domain_case = ArgumentCase(arg_id=datetime.now().microsecond,
                                                     creation_date=datetime.now().strftime(DATE_FORMAT),
                                                     problem=argument_problem,
                                                     justification=argument_justification,
                                                     solution=argument_solution)
            # Add argument case with the domain cases to the list of potential attacks
            arg_cases.append(SimilarArgumentCase(arg_case_from_domain_case, self.domain_cbr.get_premises_similarity(
                my_pos_premises, self.current_position.domain_cases[i].problem.context.premises
            )))

        # This list contains positions that represent the different argument-cases
        # extracted just to calculate the degrees with the function get_degrees() TODO almost duplicated code
        all_positions: List[Position] = []
        for similar_argument_case in arg_cases:
            solution = Solution(similar_argument_case.case.solutions.conclusion,
                                similar_argument_case.case.solutions.value,
                                similar_argument_case.case.solutions.times_used)
            all_positions.append(Position(agent_id="", dialogue_id="", solution=solution,
                                          premises=similar_argument_case.case.problem.context.premises,
                                          domain_cases=None, domain_case_similarity=1.0))
        for similar_argument_case in arg_cases:
            solution = Solution(similar_argument_case.case.solutions.conclusion,
                                similar_argument_case.case.solutions.value,
                                similar_argument_case.case.solutions.times_used)
            degrees_list = self.arg_cbr.get_degrees(arg_problem=similar_argument_case.case.problem,
                                                    solution=solution, all_positions=all_positions,
                                                    index=arg_cases.index(similar_argument_case))
            persuasiveness_degree = degrees_list[0]
            support_degree = degrees_list[1]
            risk_degree = degrees_list[2]
            attack_degree = degrees_list[3]
            efficiency_degree = degrees_list[4]
            explanatory_power = degrees_list[5]
            # SF =( (wPD * PD + wSD * SD + wRD * (1 - RD) + wAD * (1 - AD) + wED * ED + wEP * EP) ) / 6
            arg_suitability_factor = (self.wpd * persuasiveness_degree + self.wsd * support_degree + self.wrd
                                      * (1 - risk_degree) + self.wad * (
                                          1 - attack_degree) + self.wed * efficiency_degree
                                      + self.wed * explanatory_power)
            # Assign weights in accordance with the quantity of knowledge of each type
            domain_cases_num = len(self.similar_domain_cases)
            argument_cases_num = len(self.arg_cbr.get_same_domain_domain_and_social_context_accepted(
                my_pos_premises, sol, social_context))
            total_cases = domain_cases_num + argument_cases_num
            if total_cases:
                self.w_similarity = domain_cases_num / total_cases
                self.w_arg_suit_factor = argument_cases_num / total_cases
            else:
                self.w_similarity = 0.5
                self.w_arg_suit_factor = 0.5
            # Calculate suitability degree: with the current similarity in similar_argument_case,
            # and the suitability obtained from the ArgumentationCBR
            similar_argument_case.similarity = arg_suitability_factor * self.w_arg_suit_factor + \
                                               similar_argument_case.similarity * self.w_similarity

            arg_cases = sorted(arg_cases)
            inc_support_set = inc_argument.support_set
            attack: Optional[Argument] = None
            support = False
            if (not inc_support_set.premises and not inc_support_set.exceptions and not inc_support_set.presumptions
                and not inc_support_set.counter_examples_arg_cases and not inc_support_set.counter_examples_dom_cases):
                support = True

            if support:
                # Incoming argument is a support argument
                # Attack argumentation scheme
                if inc_support_set.domain_cases:
                    attack = self.generate_cea_attack(arg_cases,
                                                      inc_support_set.domain_cases[0].problem.context.premises,
                                                      relation, agent_id)
                    if not attack:
                        attack = self.generate_dp_attack(arg_cases,
                                                         inc_support_set.domain_cases[0].problem.context.premises,
                                                         relation, agent_id)
                elif not inc_support_set.argument_cases:
                    attack = self.generate_cea_attack(arg_cases,
                                                      inc_support_set.argument_cases[0].problem.context.premises,
                                                      relation, agent_id)
                    if not attack:
                        attack = self.generate_dp_attack(arg_cases,
                                                         inc_support_set.argument_cases[0].problem.context.premises,
                                                         relation, agent_id)
                else:
                    premises_dict = {premise.id: premise for premise in inc_support_set.premises}
                    attack = self.generate_dp_attack(arg_cases, premises_dict, relation, agent_id)
                    if not attack:
                        attack = self.generate_cea_attack(arg_cases, premises_dict, relation, agent_id)

            else:
                # Incoming argument is an attack argument
                # Attack argumentation scheme
                if inc_support_set.counter_examples_dom_cases:
                    attack = self.generate_cea_attack(arg_cases,
                                                      inc_support_set.counter_examples_dom_cases[0].problem.context.
                                                      premises, relation, agent_id)
                    if not attack:
                        attack = self.generate_dp_attack(arg_cases,
                                                         inc_support_set.counter_examples_dom_cases[0].problem.context.
                                                         premises, relation, agent_id)
                elif not inc_support_set.counter_examples_arg_cases:
                    attack = self.generate_cea_attack(arg_cases,
                                                      inc_support_set.counter_examples_arg_cases[0].problem.context.
                                                      premises, relation, agent_id)
                    if not attack:
                        attack = self.generate_dp_attack(arg_cases,
                                                         inc_support_set.counter_examples_arg_cases[0].problem.context.
                                                         premises, relation, agent_id)
                else:
                    premises_dict = {premise.id: premise for premise in inc_support_set.dist_premises}
                    attack = self.generate_dp_attack(arg_cases, premises_dict, relation, agent_id)
                    if not attack:
                        attack = self.generate_cea_attack(arg_cases, premises_dict, relation, agent_id)
            if attack:
                attack.attacking_to_arg_id = inc_argument.id
            return attack
        return None

    def generate_dp_attack(self, arg_cases: List[SimilarArgumentCase], its_premises: Mapping[int, Premise],
                        relation: DependencyRelation, agent_id: str) -> Optional[Argument]:
        """Return a distinguishing premises attack argument against the agent of the
        given agent identifier, and its given premises

        Args:
            arg_cases (List[SimilarArgumentCase]): list of similar argument cases to
                the given position to defend to generate the distinguishing premises
            its_premises (Mapping[int, Premise]): Dictionary of the premises of the other agent to attack
            relation (DependencyRelation): Dependency relation with the other agent to attack
            agent_id (str): The identifier of the agent to attack

        Returns:
            Optional[Argument]: Counter example attack argument, or None if it's not possible
        """
        his_useful_premises = self.get_useful_premises(self.current_problem.context.premises, its_premises)
        for similar_arg_case in arg_cases:
            my_premises =similar_arg_case.case.problem.context.premises
            my_useful_premises = self.get_useful_premises(self.current_problem.context.premises, my_premises)
            dist_premises = self.get_distinguishing_premises(my_useful_premises, his_useful_premises)
            its_dist_premises = self.get_distinguishing_premises(his_useful_premises, my_useful_premises)

            if dist_premises and len(dist_premises) > len(its_dist_premises):  # Generate attack
                premises = [premise for premise in self.current_position.premises.values()]
                domain_cases_aux: List[DomainCase] = []
                argument_cases_aux: List[ArgumentCase] = []
                schemes: List[ArgumentationScheme] = []
                dist_premises: List[Premise] = []
                presumptions: List[Premise] = []
                exceptions: List[Premise] = []
                counter_examples_domain_cases: List[DomainCase] = []
                counter_examples_argument_cases: List[ArgumentCase] = []
                support_set = SupportSet(premises, domain_cases_aux, argument_cases_aux, schemes, dist_premises,
                                         presumptions, exceptions, counter_examples_domain_cases,
                                         counter_examples_argument_cases)
                argument = Argument(datetime.now().microsecond, self.current_position.solution.conclusion,
                                    self.current_position.solution.times_used,
                                    self.current_position.solution.value, support_set, relation)

                if not self.argument_previously_used(argument, self.my_used_attack_arguments.get(agent_id)):
                    premise_str = ""
                    for premise in dist_premises:
                        premise_str += "{}={} ".format(premise.id, premise.content)
                    premise_str2 = ""
                    for premise in its_dist_premises:
                        premise_str2 += "{}={} ".format(premise.id, premise.content)
                    logger.info("{}: distinguishing premises attack argument against: {}\n my_dist_premises ({}):{}\
                                \nits_dist_premises ({}):{}".format(self.name, agent_id, len(dist_premises),
                                                                    premise_str, len(its_dist_premises), premise_str2))
                    return  argument
        return None

    def generate_cea_attack(self, arg_cases: List[SimilarArgumentCase], its_case_premises: Mapping[int, Premise],
                            relation: DependencyRelation, agent_id: str) -> Optional[Argument]:
        """Return a counter example attack argument against the agent of the
        given agent identifier, and its given premises

        Args:
            arg_cases (List[SimilarArgumentCase]): list of similar argument cases to
                the given position to defend to generate the counter examples
            its_case_premises (Mapping[int, Premise]): Dictionary of the premises of the other agent to attack
            relation (DependencyRelation): Dependency relation with the other agent to attack
            agent_id (str): The identifier of the agent to attack

        Returns:
            Optional[Argument]: Counter example attack argument, or None if it's not possible
        """
        its_useful_premises = self.get_useful_premises(self.current_problem.context.premises, its_case_premises)
        for similar_argument_case in arg_cases:
            my_premises = similar_argument_case.case.problem.context.premises
            my_useful_premises = self.get_useful_premises(self.current_problem.context.premises, my_premises)

            find = False
            for his_premise in its_useful_premises.values():
                if not my_useful_premises.get(his_premise.id):
                    find = True

            if find:
                premises: List[Premise] = [premise for premise in self.current_position.premises.values()]
                domain_cases_aux: List[DomainCase] = []
                argument_cases_aux: List[ArgumentCase] = []
                schemes: List[ArgumentationScheme] = []
                dist_premises: List[Premise] = []
                presumptions: List[Premise] = []
                exceptions: List[Premise] = []
                counter_examples_domain_cases: List[DomainCase] = []
                counter_examples_argument_cases: List[ArgumentCase] = [similar_argument_case.case]
                support_set = SupportSet(premises, domain_cases_aux, argument_cases_aux, schemes, dist_premises,
                                         presumptions, exceptions, counter_examples_domain_cases,
                                         counter_examples_argument_cases)
                argument = Argument(datetime.now().microsecond, self.current_position.solution.conclusion,
                                    self.current_position.solution.times_used,
                                    self.current_position.solution.value, support_set, relation)
                if not self.argument_previously_used(argument, self.my_used_attack_arguments.get(agent_id)):
                    logger.info("{}: counter example attack argument against: {}\n".format(self.name, agent_id))
                    return argument
        return None

    def argument_previously_used(self, arg: Argument, my_arguments: List[Argument]) -> bool:
        """Checks whether the given argument is contained in the given list of arguments or not

        Args:
            arg (Argument): The argument to be test if its knowledge resources have been used previously
            my_arguments (List[Argument]): List of arguments used previously

        Returns:
            bool: True if the given argument is contained, False otherwis
        """
        if not my_arguments:
            return False

        for i in range(len(my_arguments)-1, -1, -1):
            current_arg = my_arguments[i]
            if arg.conclusion.id == current_arg.conclusion.id and arg.value == current_arg.value:
                arg_support = arg.support_set
                current_arg_support = current_arg.support_set

                if (arg_support.argument_cases and current_arg_support.argument_cases
                    and len(arg_support.argument_cases) == len(current_arg_support.argument_cases)
                    and arg_support.argument_cases[0] == current_arg_support.argument_cases[0]):
                    logger.info("{}: SAME argument cases\n".format(self.name))
                    return True

                if (arg_support.domain_cases and current_arg_support.domain_cases
                    and len(arg_support.domain_cases) == len(current_arg_support.domain_cases)
                        and arg_support.domain_cases[0] == current_arg_support.domain_cases[0]):
                    logger.info("{}: SAME domain cases\n".format(self.name))
                    return True

                if (arg_support.counter_examples_dom_cases and current_arg_support.counter_examples_dom_cases
                    and len(arg_support.counter_examples_dom_cases) == len(current_arg_support.
                                                                           counter_examples_dom_cases)
                    and arg_support.counter_examples_dom_cases[0] == current_arg_support.
                        counter_examples_dom_cases[0]):
                    logger.info("{}: SAME counter example domain cases\n".format(self.name))
                    return True

                if (arg_support.counter_examples_arg_cases and current_arg_support.counter_examples_arg_cases
                    and len(arg_support.counter_examples_arg_cases) == len(current_arg_support.
                                                                           counter_examples_arg_cases)):
                    case1 = arg_support.counter_examples_arg_cases[0]
                    case2 = current_arg_support.counter_examples_arg_cases[0]
                    if case1.id == case2.id:
                        logger.info("{}: SAME counter example argument cases ID".format(self.name))
                        return True
                    elif (self.are_same_premises(case1.problem.context.premises, case2.problem.context.premises)
                          and case1.solutions.conclusion == case2.solutions.conclusion
                          and case1.solutions.value == case2.solutions.value
                            and case1.solutions.times_used == case2.solutions.times_used):
                        logger.info("{}: SAME counter example argument cases premises and conclusion".format(self.name))
                        return True

                if (arg_support.dist_premises and current_arg_support.dist_premises
                    and len(arg_support.dist_premises) == len(current_arg_support.dist_premises)
                    and self.are_same_premises(arg_support.dist_premises, current_arg_support.dist_premises)):
                    logger.info("{}: SAME distinguising premises".format(self.name))
                    return True

        logger.info("{}: SAME argument not previously used".format(self.name))
        return False

    @staticmethod
    def are_same_premises(premises1: Union[Mapping[int, Premise], List[Premise]],
                          premises2: Union[Mapping[int, Premise], List[Premise]]) -> bool:
        """Determines whether the premises given premises are the same

        Args:
            premises1 (Union[Mapping[int, Premise]]): Premises to be compared
            premises2 (Union[Mapping[int, Premise]]): The premises to compare with

        Returns:
            bool: True if the premises are the same, False otherwise
        Raises;
            TypeError: When the types of premises1 and premises2 don't match or are not valid
        """
        if type(premises2) != type(premises1):
            raise TypeError
        if len(premises1) != len(premises2):
            return False
        if type(premises1) == List[Premise]:
            return all([prem1 == premises2.get(prem1.id) for prem1 in premises2.values()])
        elif type(premises1) == Mapping[int, Premise]:
            for prem1 in premises2:
                if prem1 not in premises2:
                    return False
        else:
            raise TypeError
        return True

    @staticmethod
    def get_useful_premises(problem_premises: Mapping[int, Premise], my_premises: Mapping[int, Premise]) -> \
            Dict[int, Premise]:
        """Returns a dictionary of the useful premises of the agent of the current problem to solve
        (the premises of the position that are specified in the problem characterisation).

        Args:
            problem_premises (Mapping[int, Premise]): Dictionary with the premises of the problem to solve
            my_premises (Mapping[int, Premise]): Dictionary with the premises of the
                position that defends the agent

        Returns:
            Dict[int, Premise]: Dictionary of the useful premises of the agent of the
                current problem to solve
        """
        return {premise.id: premise
                for premise in my_premises.values() if problem_premises.get(premise.id)
                and problem_premises.get(premise.id).content == premise.content}

    @staticmethod
    def get_distinguishing_premises(my_premises: Mapping[int, Premise], its_premises: Mapping[int, Premise]) -> \
            List[Premise]:
        """Returns a list with distinguishing premises between the dictionaries given as arguments

        Args:
            my_premises (Mapping[int, Premise]): Dictionary with the premises candidates to be distinguishing premises
            its_premises (Mapping[int, Premise]): Dictionary with the premises to generate
                distinguishing premises against

        Returns:
            List[Premise]: List with distinguishing premises
        """
        return [premise for premise in my_premises.values()
                if not (its_premises.get(premise.id) and its_premises.get(premise.id).content == premise.content)]

    def add_position(self, pos: Position, dialogue_id: str) -> ArgMessage:
        """Returns a message with the performative ADD_POSITION_PERF and the position proposed
        to send to the commitment store

        Args:
            pos: Position to add to the commitment store
            dialogue_id: The dialogue identifier

        Returns:
            The message to be sent
        """
        self.my_used_locutions += 1
        return self.create_message(self.commitment_store_id, ADD_POSITION_PERF, dialogue_id, None)

    def enter_dialogue_cs(self, dialogue_id: str) -> ArgMessage:
        """Returns a message with the performative ENTER_DIALOGUE_PERF to send to the commitment store

        Args:
            dialogue_id (str): ID of the dialogue to engage in

        Returns:
            ArgMessage: The message to be sent
        """
        self.my_used_locutions += 1
        return self.create_message(self.commitment_store_id, ENTER_DIALOGUE_PERF, dialogue_id, None)

    def get_preferred_value_index(self, value: str) -> int:
        """Returns the index of the given preference value

        Args:
            value (str): String representing a preference value

        Returns:
            int: The index of the given preference value, -1 if not is contained
        """
        try:
            return self.prefered_values.index(value)
        except ValueError:
            return -1

    def get_friend_index(self, agent_id: str) -> int:
        """Returns the index of the given agent identifier

        Args:
            agent_id (str): The identifier of the agent

        Returns:
            int: the index of the given agent, -1 if does not exist
        """
        index = 0
        for friend in self.my_friends:
            if friend.name == agent_id:
                return index
            index += 1
        return -1

    def get_different_positions(self):
        pass

    def create_message(self, agent_id: str, performative: str, dialogue_id: str, content_object: Optional[Any]) -> \
        ArgMessage:
        """Creates and returns an message with the given arguments.

        Args:
            agent_id (str): The agent ID to send the message to
            performative (str): The performative for the message
            dialogue_id (str): The dialogue ID
            content_object (Any): The object to be attached to the message

        Returns:
            ArgMessage: The message to be sent
        """
        msg = ArgMessage()
        msg.sender = self.my_id
        msg.to.append(agent_id)
        if performative == NO_COMMIT_PERF or performative == ASSERT_PERF or performative == ATTACK_PERF:
            msg.to.append(self.commitment_store_id)
        msg.set_metadata(CONVERSATION, dialogue_id)

        if '=' in performative:
            index = performative.index("=")
            content_agent_id = performative[index + 1:]
            performative = performative[:index]
            msg.set_metadata("agent_id", content_agent_id)
        msg.set_metadata(PERFORMATIVE, performative)

        if content_object:
            msg.body = MessageCodification.pickle_object(content_object)

        receivers_str = ""
        for receiver in msg.to:
            receivers_str += receiver[:receiver.index("@")] + " "

        logger.info("{} message to send to: {} | performative: {}", self.name, receivers_str,
                    msg.get_metadata(PERFORMATIVE))
        return msg


class ArgBehaviour(FSMBehaviour):
    agent: ArgAgent

    async def send(self, msg: ArgMessage):
        for receiver in msg.to:
            yield await super().send(Message(to=receiver, sender=msg.sender, metadata=msg.metadata, body=msg.body))

    def __init__(self):
        super().__init__()

    async def on_start(self):
        logger.info("Starting ArgBehaviour of {}".format(self.agent.my_id))

    def do_respond(self, msg: Optional[Message]) -> Optional[Message]:
        pass

    async def run(self):
        pass
