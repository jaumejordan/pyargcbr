from datetime import datetime
from random import random
from typing import List, Dict, Optional, Any, Mapping, Union

from loguru import logger
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message

from .protocol import ADD_POSITION_PERF, \
    GET_ALL_POSITIONS_PERF, NO_COMMIT_PERF, ASSERT_PERF, ATTACK_PERF, ENTER_DIALOGUE_PERF, WITHDRAW_DIALOGUE_PERF, \
    DIE_PERF, \
    ACCEPT_PERF, PERFORMATIVE, CONVERSATION, WHY_PERF, \
    MSG_TIMEOUT, OPEN_DIALOGUE_PERF, MessageCodification as msg_cod, ACCEPTS_PERF, FINISH_DIALOGUE_PERF, \
    ATTACKS_PERF, ASSERTS_PERF
from ..agents.arg_message import ArgMessage
from ..cbrs.argumentation_cbr import ArgCBR
from ..cbrs.domain_cbr import DomainCBR
from ..knowledge_resources.acceptability_status import AcceptabilityStatus
from ..knowledge_resources.arg_node import ArgNode, NodeType
from ..knowledge_resources.argument import Argument
from ..knowledge_resources.argument_case import ArgumentCase
from ..knowledge_resources.argument_justification import ArgumentJustification
from ..knowledge_resources.argument_problem import ArgumentProblem
from ..knowledge_resources.argument_solution import ArgumentSolution, ArgumentType
from ..knowledge_resources.argumentation_scheme import ArgumentationScheme
from ..knowledge_resources.dialogue_graph import DialogueGraph
from ..knowledge_resources.domain_case import DomainCase
from ..knowledge_resources.domain_context import DomainContext
from ..knowledge_resources.group import Group
from ..knowledge_resources.position import Position
from ..knowledge_resources.premise import Premise
from ..knowledge_resources.problem import Problem
from ..knowledge_resources.similar_argument_case import SimilarArgumentCase
from ..knowledge_resources.similar_domain_case import SimilarDomainCase
from ..knowledge_resources.social_context import DependencyRelation, SocialContext
from ..knowledge_resources.social_entity import SocialEntity
from ..knowledge_resources.solution import Solution
from ..knowledge_resources.support_set import SupportSet

DATE_FORMAT = "%m/%d/%Y, %H:%M:%S"
BEGIN_STATE = "BEGIN_STATE"
OPEN_STATE = "OPEN_STATE"
DIE_STATE = "DIE_STATE"
ENTER_STATE = "ENTER_STATE"
PROPOSE_STATE = "PROPOSE_STATE"
CENTRAL_STATE = "CENTRAL_STATE"
ASSERT_STATE = "ASSERT_STATE"
WAIT_ATTACK_STATE = "WAIT_ATTACK_STATE"
DEFEND_STATE = "DEFEND_STATE"
QUERY_POSITIONS_STATE = "QUERY_POSITIONS_STATE"
GET_POSITIONS_STATE = "GET_POSITIONS_STATE"
SEND_POSITION_STATE = "SEND_POSITION_STATE"
SOLUTION_STATE = "SOLUTION_STATE"
WHY_STATE = "WHY_STATE"
WAIT_ASSERT_STATE = "WAIT_ASSERT_STATE"
ATTACK_STATE = "ATTACK_STATE"
ATTACK2_STATE = "ATTACK2_STATE"


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
                 ini_domain_cases_file_path: str, fin_domain_cases_file_path: str,
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
        self.different_positions: Optional[List[Position]] = None

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
        self.my_support_arguments: Dict[str, List[Argument]] = {}
        self.my_used_locutions: int = 0  # TODO locutions or performatives

        self.my_used_support_arguments: Dict[str, List[Argument]] = {}
        self.my_used_attack_arguments: Dict[str, List[Argument]] = {}

        self.store_arguments: Dict[str, List[Argument]] = {}

        self.current_why_agent_id: Optional[str] = None

    async def setup(self):
        fsm = ArgBehaviour()
        fsm.add_state(name=BEGIN_STATE, state=BeginState(), initial=True)
        fsm.add_state(name=OPEN_STATE, state=OpenState())
        fsm.add_state(name=DIE_STATE, state=DieState())
        fsm.add_state(name=ENTER_STATE, state=EnterState())
        fsm.add_state(name=PROPOSE_STATE, state=ProposeState())
        fsm.add_state(name=CENTRAL_STATE, state=CentralState())
        fsm.add_state(name=ASSERT_STATE, state=AssertState())
        fsm.add_state(name=WAIT_ATTACK_STATE, state=WaitAttackState())
        fsm.add_state(name=DEFEND_STATE, state=DefendState())
        fsm.add_state(name=QUERY_POSITIONS_STATE, state=QueryPositionsState())
        fsm.add_state(name=GET_POSITIONS_STATE, state=GetPositionsState())
        fsm.add_state(name=SEND_POSITION_STATE, state=SendPositionState())
        fsm.add_state(name=SOLUTION_STATE, state=SolutionState())
        fsm.add_state(name=WHY_STATE, state=WhyState())
        fsm.add_state(name=WAIT_ASSERT_STATE, state=WaitAssertState())
        fsm.add_state(name=ATTACK_STATE, state=AttackState())
        fsm.add_state(name=ATTACK2_STATE, state=Attack2State())
        # Transitions from one state to itself are not necessary to add like this TODO aren't they?
        fsm.add_transition(source=BEGIN_STATE, dest=OPEN_STATE)
        fsm.add_transition(source=OPEN_STATE, dest=DIE_STATE)
        fsm.add_transition(source=OPEN_STATE, dest=ENTER_STATE)
        fsm.add_transition(source=ENTER_STATE, dest=PROPOSE_STATE)
        fsm.add_transition(source=ENTER_STATE, dest=OPEN_STATE)
        fsm.add_transition(source=PROPOSE_STATE, dest=OPEN_STATE)
        fsm.add_transition(source=PROPOSE_STATE, dest=CENTRAL_STATE)
        fsm.add_transition(source=CENTRAL_STATE, dest=ASSERT_STATE)
        fsm.add_transition(source=CENTRAL_STATE, dest=QUERY_POSITIONS_STATE)
        fsm.add_transition(source=CENTRAL_STATE, dest=SEND_POSITION_STATE)
        fsm.add_transition(source=SEND_POSITION_STATE, dest=SOLUTION_STATE)
        fsm.add_transition(source=SOLUTION_STATE, dest=OPEN_STATE)
        fsm.add_transition(source=ASSERT_STATE, dest=WAIT_ATTACK_STATE)
        fsm.add_transition(source=ASSERT_STATE, dest=CENTRAL_STATE)
        fsm.add_transition(source=ASSERT_STATE, dest=PROPOSE_STATE)
        fsm.add_transition(source=WAIT_ATTACK_STATE, dest=CENTRAL_STATE)
        fsm.add_transition(source=WAIT_ATTACK_STATE, dest=DEFEND_STATE)
        fsm.add_transition(source=DEFEND_STATE, dest=WAIT_ATTACK_STATE)
        fsm.add_transition(source=DEFEND_STATE, dest=PROPOSE_STATE)
        fsm.add_transition(source=QUERY_POSITIONS_STATE, dest=GET_POSITIONS_STATE)
        fsm.add_transition(source=GET_POSITIONS_STATE, dest=WHY_STATE)
        fsm.add_transition(source=GET_POSITIONS_STATE, dest=SEND_POSITION_STATE)
        fsm.add_transition(source=GET_POSITIONS_STATE, dest=CENTRAL_STATE)
        fsm.add_transition(source=WHY_STATE, dest=CENTRAL_STATE)
        fsm.add_transition(source=WHY_STATE, dest=WAIT_ASSERT_STATE)
        fsm.add_transition(source=WAIT_ASSERT_STATE, dest=CENTRAL_STATE)
        fsm.add_transition(source=WAIT_ASSERT_STATE, dest=ATTACK_STATE)
        fsm.add_transition(source=ATTACK_STATE, dest=ATTACK2_STATE)
        fsm.add_transition(source=ATTACK_STATE, dest=CENTRAL_STATE)
        fsm.add_transition(source=ATTACK2_STATE, dest=CENTRAL_STATE)

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

    def no_commit(self, agent_id: str) -> ArgMessage:
        """Returns a message with the performative NO_COMMIT_PERF to challenge the given position

        Args:
            agent_id (str): Agent identifier to tell NO_COMMIT

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
                    efficiency_degree = degrees[4]
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
            return final_support_arguments
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
            return None

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
        # extracted just to calculate the degrees with the function get_degrees()
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
            my_premises = similar_arg_case.case.problem.context.premises
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
                    return argument
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

        for i in range(len(my_arguments) - 1, -1, -1):
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

    def get_different_positions(self, positions: List[Position]) -> List[Position]:
        """Returns a list of positions that are different from the defended
        position and also are not asked yet

        Args:
            positions (List[Position]): List with all the positions in the dialogue

        Returns:
            List[Position]: List of positions that are different from the defended position
        """
        if not positions:
            return []
        different_positions = []
        # If it has not position, all positions are considered different
        if not self.current_position:
            return positions
        for pos in positions:
            asked = False
            for asked_pos in self.asked_positions:
                if asked_pos:
                    asked_pos_agent_id = asked_pos.agent_id
                    pos_agent_id = pos.agent_id
                    if (pos_agent_id == asked_pos_agent_id
                        and asked_pos.solution.conclusion.id == pos.solution.conclusion.id
                        and asked_pos.solution.value == pos.solution.value):
                        logger.info("{}: position already asked".format(self.name))
                        asked = True
                        break
            if not asked:
                different_positions.append(pos)
        return different_positions

    def enter_dialogue_cs(self, dialogue_id: str) -> ArgMessage:
        """Returns a message with the performative ENTER_DIALOGUE_PERF to send to the commitment store

        Args:
            dialogue_id (str): ID of the dialogue to engage in

        Returns:
            ArgMessage: The message to be sent
        """
        self.my_used_locutions += 1
        return self.create_message(self.commitment_store_id, ENTER_DIALOGUE_PERF, dialogue_id, None)

    @staticmethod
    def domain_cases_to_int_ids(domain_cases: List[DomainCase]) -> List[int]:
        """Returns the list of IDs of the given domain cases

        Args:
            domain_cases (List[DomainCase]): The domain cases to get the IDs from

        Returns:
            List[int]: The list of IDs of the given domain cases
        """
        return [case.id for case in domain_cases]

    @staticmethod
    def argument_cases_to_int_ids(argument_cases: List[ArgumentCase]) -> List[int]:
        """Returns the list of IDs of the givenargument cases

        Args:
            argument_cases (List[ArgumentCase]): The argument cases to get the IDs from

        Returns:
            List[int]: The list of IDs of the given argument cases
        """
        return [case.id for case in argument_cases]

    def update_case_bases(self, solution: Solution):
        """ Adds the final solution to the current problem and adds it in the domain cases case base.
        Also, stores all the generated argumentation data in the argument cases case base.
        Finally, makes a cache of the domain CBR and the argumentation CBR

        Args:
            solution (Solution): The final solution to the current problem
        """
        # Add the solution to the ticket and add the ticket to domainCBR
        solutions = [solution]
        case_added = self.domain_cbr.add_case(self.current_dom_case_to_solve)
        if case_added:
            logger.info("{}: Domain case Introduced".format("self.name"))
        else:
            logger.info("{}: Domain case Not Introduced".format("self.name"))

        # Add argument-cases generated during the dialogue
        domain_context = DomainContext(self.current_dom_case_to_solve.problem.context.premises)
        index = 0
        for friend in self.my_friends:
            relation = self.dependency_relations[index]
            social_context = SocialContext(self.my_social_entity, friend, self.my_group, relation)
            dialogues = self.dialogue_graphs.get(friend.name)

            # Support argument
            list_args = self.store_arguments.get(friend.name, [])
            for arg in list_args:
                argument_problem = ArgumentProblem(domain_context, social_context)
                # TODO are these soft copies enough? There are more all over the code. Tests will tell
                dist_premises = [p for p in arg.received_attacks_dist_premises]
                counter_example_dom = self.domain_cases_to_int_ids(
                    [c_ex_dom for c_ex_doms in arg.received_attacks_counter_examples for c_ex_dom in
                     c_ex_doms.support_set.counter_examples_dom_cases])
                counter_example_arg = self.argument_cases_to_int_ids(
                    [c_ex_arg for c_ex_args in arg.received_attacks_counter_examples for c_ex_arg in
                     c_ex_args.support_set.counter_examples_arg_cases])
                # Put presumptions and exceptions
                argument_solution = ArgumentSolution(argument_type=ArgumentType.INDUCTIVE,
                                                     acceptability_status=arg.acceptability_state, value=arg.value,
                                                     dist_premises=dist_premises, times_used=arg.times_used_conclusion,
                                                     presumptions=[], exceptions=[], conclusion=arg.conclusion,
                                                     counter_examples_arg_case_id=counter_example_dom,
                                                     counter_examples_dom_case_id=counter_example_arg)
                domain_cases_ids = [dom_case.id for dom_case in arg.support_set.domain_cases]
                argument_cases_ids = [arg_case.id for arg_case in arg.support_set.argument_cases]
                # Take the dialogues where this argument is implied
                diags: List[DialogueGraph] = []
                if dialogues:
                    diags = [d for d in dialogues if arg.id in d]

                argument_justification = ArgumentJustification(domain_cases_ids=domain_cases_ids,
                                                               argument_cases_ids=argument_cases_ids, schemes=
                                                               arg.support_set.schemes, dialogue_graphs=diags)
                new_argument_case = ArgumentCase(arg.id, datetime.now().strftime(DATE_FORMAT), argument_problem,
                                                 argument_solution, argument_justification)
                case_added = self.arg_cbr.add_case(new_argument_case)
                if case_added:
                    logger.info("{}: friend={}({}) -> Argument case Introduced".format(self.name, index, friend.name))
                else:
                    logger.info("{}: friend={}({}) -> Argument case Updated".format(self.name, index, friend.name))
            index += 1

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
            msg.body = msg_cod.pickle_object(content_object)

        receivers_str = ""
        for receiver in msg.to:
            receivers_str += receiver[:receiver.index("@")] + " "

        logger.info("{} message to send to: {} | performative: {}", self.name, receivers_str,
                    msg.get_metadata(PERFORMATIVE))
        return msg

    def do_propose(self, msg: Message) -> bool:
        """
        Proposes a position to defend in the dialogue. If it can not, it does a withdraw dialogue

        Args:
            msg (Message): Message to send with the position to propose (ADD_POSITION_PERF) or WITHDRAW_DIALOGUE_PERF

        Returns:
            bool: True if it makes an ADD_POSITION_PERF, False if it makes a WITHDRAW_DIALOGUE_PERF
        """
        if not self.positions_generated:
            self.my_positions = self.generate_positions(self.current_problem)
        self.current_position = None
        if self.my_positions:
            self.current_position = self.my_positions.pop(
                0)  # Extract the first and remove it from the list
            if self.current_position:
                self.last_position_before_none = Position(self.current_position.agent_id,
                                                          self.current_position.dialogue_id,
                                                          self.current_position.solution,
                                                          self.current_position.premises,
                                                          self.current_position.domain_cases,
                                                          self.current_position.domain_case_similarity)
            self.current_pos_accepted = 0
            self.my_support_arguments = {}
            self.my_used_support_arguments = {}
            self.my_used_attack_arguments = {}
            self.current_dialogue_graph = None
        if self.current_position:
            msg = self.propose(self.current_position, self.current_dialogue_id)
            logger.info("{}::propose::{}\n".format(self.my_id, self.current_position.solution.conclusion.description))
            return True
        else:
            msg = self.withdraw_dialogue()
            logger.info("{}::withdraw::\n".format(self.my_id))
            return False

    def do_assert(self, msg: Message, why_agent_id: str) -> str:
        """
        Try to assert a support argument to respond to the WHY received previously

        Args:
            msg (Message): Message to send with an argument and locution ASSERT_PERF, a performative NO_COMMIT_PERF, or a performative NOTHING_PERF
            why_agent_id (str): Agent identifier that has made the WHY_PERF

        Returns:
            str: String describing if it makes an ASSERT_PERF, NO_COMMIT_PERF or, WAIT_CENTRAL_PERF
        """
        logger.info("{}<-{}::why::{}\n".format(self.my_id, why_agent_id,
                                               self.current_position.solution.conclusion.description))
        # Clean other possible WHY sent by the same agent and attend only one
        my_positions_asked = self.attended_why_petitions.get(why_agent_id)
        if my_positions_asked and self.current_position in my_positions_asked:
            # I have already replied this agent with my current position, do not reply him
            return CENTRAL_STATE  # send message with performative NOTHING_PERF to noOne (non existing agent)
        else:
            # try to generate a support argument with:
            # 1) Argument-cases 2) domain-cases 3) premises
            support_args = self.generate_support_arguments(self.current_position, why_agent_id)
            arg: Optional[Argument] = None
            if support_args:
                arg = support_args.pop(0)
            self.my_support_arguments[why_agent_id] = support_args
            if arg:  # Assert the argument
                logger.info("***************{} received WHY_PERF, generating support arg. ASSERTING".format(self.my_id))
                logger.info("{}->{}::assert::{}\n".format(self.my_id, why_agent_id,
                                                          self.current_position.solution.conclusion))
                msg = self.asserts(why_agent_id, arg)
                # I am now talking only with this agent
                self.sub_dialogue_agent_id = why_agent_id

                # Add argument to myUsedSupportArguments
                support_args_used = self.my_used_support_arguments
                if not support_args_used:
                    support_args_used = []
                support_args_used.append(arg)
                self.my_used_support_arguments[why_agent_id] = support_args_used

                # Add argument to dialogue graph, it is the first
                arg_node = ArgNode(arg.id, [], -1, NodeType.FIRST)
                current_dialogue_graph = DialogueGraph()
                current_dialogue_graph.add_node(arg_node)

                return ASSERT_PERF
            else:  # Can not generate support arguments, no commit
                logger.info("***************{} received WHY_PERF, generating support arg. NO_COMMIT".format(self.my_id))
                msg = self.no_commit(why_agent_id, self.current_position)
                return NO_COMMIT_PERF

    def do_attack(self, msg_to_send: ArgMessage, msg_received: Message, defending: bool) -> bool:
        """Actions to perform to generate an attack argument against an attack or assert received

        Args:
            msg_to_send (ArgMessage): Message to send with the attack argument or a NO_COMMIT_PERF
            msg_received (Message): Message received with an attack or assert
            defending (bool): Bool that indicates if it is defending its position or attacking another agent position

        Returns:
            bool: True if an attack argument has been generated, False otherwise
        """
        against_argument: Argument = msg_cod.get_decoded_message_content(msg_received)
        self.sub_dialogue_agent_id = msg_received.sender

        # Store this attack into the corresponding argument
        my_last_used_arg = self.get_my_last_used_argument(self.sub_dialogue_agent_id, against_argument.
                                                          attacking_to_arg_id)
        if my_last_used_arg:
            # If attack was a counter-example
            if (against_argument.support_set.counter_examples_dom_cases
                or against_argument.support_set.counter_examples_arg_cases):
                my_last_used_arg.add_received_attacks_counter_examples(against_argument)
            else:  # It is a distinguishing premises attack
                my_last_used_arg.add_received_attacks_dist_premises(against_argument)

        arg_node = Optional[ArgNode] = None
        if msg_received.get_metadata(PERFORMATIVE) == ASSERT_PERF:
            # Add his position to my asked positions
            sol = Solution(against_argument.conclusion, against_argument.value, against_argument.times_used_conclusion)
            his_position = Position(self.sub_dialogue_agent_id, self.current_dialogue_id, sol, None, None, 0.0)
            self.asked_positions.append(his_position)
            arg_node = ArgNode(against_argument.id, [], -1, NodeType.FIRST)
            self.current_dialogue_graph = DialogueGraph()
            logger.info("{}<-{}::assert::{}\n".format(self.my_id, self.sub_dialogue_agent_id,
                                                      against_argument.conclusion.description))
        else:
            if defending:
                my_positions_asked: List[Position] = self.attended_why_petitions.get(self.sub_dialogue_agent_id, [])
                my_positions_asked.append(self.current_position)
                self.attended_why_petitions[self.sub_dialogue_agent_id] = my_positions_asked
            logger.info("{}<-{}::attack::{}\n".format(self.my_id, self.sub_dialogue_agent_id,
                                                      against_argument.conclusion.description))
            attack_node = self.current_dialogue_graph.get_node(against_argument.attacking_to_arg_id)
            if not attack_node:
                logger.error("{} sub_dialogue_agent_id {} GETTING NODE {}".format(self.my_id,
                                                                                  self.sub_dialogue_agent_id,
                                                                                  against_argument.attacking_to_arg_id))
                for node in self.current_dialogue_graph.nodes:
                    logger.error("{}: {} PARENT {}\n".format(self.my_id, node.node_type, node.parent_arg_case_id))
                for sup in self.my_used_support_arguments.keys():
                    my_supports = self.my_used_support_arguments.get(sup)
                    if my_supports:
                        for supp in my_supports:
                            logger.error("{} sub_dialogue_agent_id {} Support Argument {}".format(self.my_id, sup,
                                                                                                  supp.id))
                for att in self.my_used_attack_arguments.keys():
                    my_attacks = self.my_used_attack_arguments.get(att)
                    if my_attacks:
                        for attack in my_attacks:
                            logger.error("{} sub_dialogue_agent_id {} Support Argument {}".format(self.my_id, att,
                                                                                                  attack.id))
            else:
                attack_node.add_child_arg_node(against_argument.id)

        self.current_dialogue_graph.add_node(arg_node)
        # Try to generate an attack argument: Distinguishing premise or Counter Example,
        # depending on the attack received
        logger.info("+++++++ {} performative = {}".format(self.my_id, msg_received.get_metadata(PERFORMATIVE)))
        logger.info("+++++++ {}: do_attack from {}".format(self.my_id, self.sub_dialogue_agent_id))
        logger.info("+++++++ {} preceiver {}".format(self.my_id, msg_received.to))
        attack_argument = self.generate_attack_argument(against_argument, self.sub_dialogue_agent_id)

        if attack_argument:
            msg = self.attack(self.sub_dialogue_agent_id, attack_argument)
            # Clean message queue from old messages
            attack_arguments: List[Argument] = self.my_used_attack_arguments.get(self.sub_dialogue_agent_id, [])
            attack_arguments.append(attack_argument)
            self.my_used_attack_arguments[self.sub_dialogue_agent_id] = attack_arguments

            logger.info("\n{}: my_used_attack_args with {} {} {}\n".format(self.my_id, self.sub_dialogue_agent_id,
                                                                           len(attack_arguments), len(
                    self.my_used_attack_arguments.get(self.sub_dialogue_agent_id, []))))
            logger.info("{}->sub_dialogue_agent_id::attack::{}\n".format(self.my_id, self.sub_dialogue_agent_id,
                                                                         self.current_position.solution.conclusion.description))

            # Add the attack argument to dialogue graph
            att_node = self.current_dialogue_graph.get_node(against_argument.id)
            if not att_node:
                logger.error("{} GETTING NODE {}".format(self.my_id, against_argument.id))
                for node in self.current_dialogue_graph.nodes:
                    logger.error("{}: {} PARENT {}\n".format(self.my_id, node.node_type, node.parent_arg_case_id))
            att_node.add_child_arg_node(attack_argument.id)
            attack_node = ArgNode(attack_argument.id, [], against_argument.id, NodeType.NODE)
            self.current_dialogue_graph.add_node(attack_node)

            return True
        else:
            # If the agent cannot generate another attack, it retracts its attack argument. If it has no more attacks,
            # it has to retract the support argument, if it has no more support arguments,
            # it has to withdraw its position with a noCommit locution

            # Search my last attack argument, the one I told this agent
            attack_arguments = self.my_used_attack_arguments.get(self.sub_dialogue_agent_id)
            if attack_arguments:
                my_last_attack_arg = attack_arguments[-1]
                # Put acceptability status to Unacceptable
                my_last_attack_arg.acceptability_state = AcceptabilityStatus.UNACCEPTABLE
                # Retract my last attack argument
                store_list: List[Argument] = self.store_arguments.get(self.sub_dialogue_agent_id, {})
                store_list.append(my_last_attack_arg)
                self.store_arguments[self.sub_dialogue_agent_id] = store_list

                # Set the last node of this branch of the dialogue graph
                this_node = self.current_dialogue_graph.get_node(my_last_attack_arg.id)
                if not this_node:
                    logger.error("{} GETTING NODE {}".format(self.my_id, my_last_attack_arg.id))
                    for node in self.current_dialogue_graph.nodes:
                        logger.error("{}: {} PARENT {}\n".format(self.my_id, node.node_type, node.parent_arg_case_id))
                else:
                    this_node.node_type = NodeType.LAST

            return False

    def do_query_positions(self, msg: ArgMessage):
        """Creates a message to send to the Commitment Store with the performative GET_ALL_POSITIONS_PERF
        to obtain all the positions of the dialogue

        Args:
            msg (ArgMessage): Message to send to the Commitment Store with the performative GET_ALL_POSITIONS_PERF
        """
        msg = self.create_message(self.commitment_store_id, GET_ALL_POSITIONS_PERF, self.current_dialogue_id, None)

    def do_get_positions(self, msg: Message):
        """Get the positions of the agents in the dialogue sent by the Commitment Store as an object

        Args:
            msg (ArgMessage): Message with performative GET_ALL_POSITIONS_PERF and the positions
            of other agents in the dialogue
        """
        self.different_positions = self.get_different_positions(msg_cod.get_decoded_message_content(msg))

    def do_why(self, msg: Message) -> bool:
        """Choose a position to send a WHY_PERF message if it can, or NOTHING_PERF

        Args:
            msg (ArgMessage): Message with performative WHY_PERF or NOTHING_PERF if there is not any position to ask
        Returns:
            bool: True if it makes a WHY_PERF, False if it makes a NOTHING_PERF
        """
        if not self.different_positions:  # Some positions to ask
            rand_pos = int(random() * len(self.different_positions))
            pos = self.different_positions[rand_pos]  # position choosen randomly

            # We only add the position of the other agent when the other agent responds
            msg = self.why(pos.agent_id, pos)
            logger.info("------------ ------ {}: WHY to {}".format(self.my_id, pos.agent_id))
            logger.info("{}->{}::why::{}\n".format(self.my_id, pos.agent_id, pos.solution.conclusion.description))

            return True
        else:  # Nothing to challenge, remain in this state send NOTHING message
            logger.info("{}: NOT WHY nothing to challenge".format(self.my_id))
            return False

    def do_open_dialogue(self, msg: Message):
        """Takes the domain case to solve and the dialogue ID from the message given

        Args:
            msg (Message): Message with the domain-case to solve and the dialogue ID
        """
        self.current_dom_case_to_solve = msg_cod.get_decoded_message_content(msg)
        self.current_dialogue_id = msg.get_metadata(CONVERSATION)

    def do_enter_dialogue(self, msg: Message) -> bool:
        """Evaluates if the agent can enter in the dialogue offering a solution. If it can not,
        it does a withdraw dialogue

        Args:
            msg (Message): Message to send to Commitment Store, with performative
                ENTER_DIALOGUE_perf or WITHDRAW_DIALOGUE_PERF

        Returns:
            bool: True if it makes an ENTER_DIALOGUE_perf, False if it makes a WITHDRAW_DIALOGUE_PERF
        """
        self.agreement_reached = 0
        self.acceptance_frequency = 0
        self.used_arg_cases = 0

        msg = self.enter_dialogue(self.current_dom_case_to_solve, self.current_dialogue_id)
        perf = msg.get_metadata(PERFORMATIVE)
        logger.info("{}: message {} receiver: {}".format(self.my_id, perf, msg.to))
        if perf == ENTER_DIALOGUE_PERF:
            return True
        else:
            return False

    def finish_dialogue(self):
        """Actions to be executed when the dialogue has to finish"""
        pass

    def do_send_position(self, msg: Message):
        """Prepares a message with the position defended by the agent

        Args:
            msg: A message to send with the position defended by the agent
        """
        if self.current_position:
            msg = self.create_message(self.commitment_store_id, ADD_POSITION_PERF, self.current_dialogue_id,
                                      self.current_position)
        else:
            logger.error("{}: NONE CURRENT POSITION".format(self.my_id))

    def do_solution(self, msg: Message):
        """Actions to perform when the final solution to the current problem to solve arrives in a message

        Args:
            msg: Message received with the solution to the current problem
        """
        solution = msg_cod.get_decoded_message_content(msg)
        if solution.conclusion.id != -1:
            self.update_case_bases(solution)
        logger.info("{}: SOLUTION received from: {}\n dom_case_num={}\narg_cases_num={}".format(self.my_id, msg.sender,
                                                                                                len(
                                                                                                    self.domain_cbr.get_all_cases_list()),
                                                                                                len(
                                                                                                    self.arg_cbr.get_all_cases_list())))

    def do_die(self):
        """Actions to perform when the message with locution DIE is received"""
        self.stop()

    def do_my_position_accepted(self, msg: Message):
        """Actions to perform when the position of the agent has been accepted

        Args:
            msg (Message): Message with the performative ACCEPT_PERF TODO ACCEPT Vs ACCEPTS
        """
        # my position is accepted, increase timesAccepted of my position
        self.current_position.times_accepted += 1
        logger.info("{}: increasing vote for my position. SolID={} current votes={}\n".format(self.my_id,
                                                                                              self.current_position.solution.conclusion.id,
                                                                                              self.current_position.times_accepted))
        logger.info("{}<-{}::accept::{}::{}\n".format(self.name, msg.sender, self.current_position.solution.conclusion.
                                                      description, self.current_position.times_accepted))
        # Change my support argument acceptability status search my support argument, the one I told this agent
        support_args: List[Argument] = self.my_used_support_arguments.get(msg.sender, [])
        my_last_support_arg = support_args[-1]
        my_last_support_arg.acceptability_state = AcceptabilityStatus.ACCEPTABLE
        support_args[-1] = my_last_support_arg
        self.my_support_arguments[msg.sender] = support_args
        store_list: List[Argument] = self.store_arguments.get(msg.sender, [])
        store_list.append(my_last_support_arg)
        self.store_arguments[msg.sender] = store_list
        # Change type of the last node in dialogue graph that corresponds to the last argument that I gave
        if self.current_dialogue_graph.nodes:
            self.current_dialogue_graph.nodes[-1].node_type = NodeType.AGREE
        else:
            logger.error("{}: GETTING NODE".format(self.my_id))
            for node in self.current_dialogue_graph.nodes:
                logger.error("{}: {} PARENT {}\n".format(self.my_id, node.node_type, node.parent_arg_case_id))

        # Add finished dialogue to the dict
        these_graphs: List[DialogueGraph] = self.dialogue_graphs.get(msg.sender, [])
        these_graphs.append(self.current_dialogue_graph)
        self.dialogue_graphs[msg.sender] = these_graphs

    def do_no_commit(self, msg: Message):
        """Creates a message to send with the performative NO_COMMIT_PERF

        Args:
            msg (Message): Message to send with the performative NO_COMMIT_PERF
        """
        msg = self.no_commit(self.sub_dialogue_agent_id, self.current_position)
        logger.info("{}->{}::no_commit::\n".format(self.my_id, self.sub_dialogue_agent_id))

    def do_other_no_commit(self, msg: Message):
        """Actions to perform when the other agent does NO_COMMIT_PERF

        Args:
            msg (Message): Message received with a NO_COMMIT_PERF
        """
        logger.info("{}<-{}::no_commit::\n".format(self.my_id, self.sub_dialogue_agent_id))

    def do_accept(self, msg: Message):
        """Actions to perform and sena a message accepting the other agent's position or argument

        Args:
            msg (Message): Message accepting the other agent's position or argument
        """
        msg = self.accept(self.sub_dialogue_agent_id)
        logger.info("{}->{}::accept::\n".format(self.my_id, self.sub_dialogue_agent_id))


class ArgBehaviour(FSMBehaviour):
    async def send(self, msg: ArgMessage):
        for receiver in msg.to:  # TODO Is this the way to do it?
            yield await super().send(Message(to=receiver, sender=msg.sender, metadata=msg.metadata, body=msg.body))

    def __init__(self):
        super().__init__()

    async def on_start(self):
        logger.info("Starting ArgBehaviour of {}".format(self.agent.my_id))

    def do_respond(self, msg: Optional[Message]) -> Optional[Message]:
        pass

    async def run(self):
        pass  # TODO how to manage messages with the performatives FINISH_DIALOGUE_PERF AND DIE_PERF


class BeginState(State):
    async def on_start(self):
        logger.info("{}: Entering BeginState")

    async def run(self):
        self.next_state(OPEN_STATE)


class OpenState(State):
    agent: ArgAgent

    async def on_start(self):
        logger.info("{}: Entering OpenState")

    async def run(self):
        msg = await self.receive(timeout=MSG_TIMEOUT)
        if msg:
            perf = msg.get_metadata(PERFORMATIVE)
            if perf == DIE_PERF:
                self.next_state(DIE_STATE)
            elif perf == OPEN_DIALOGUE_PERF:
                self.agent.do_open_dialogue(msg)
                self.next_state(ENTER_STATE)


class EnterState(State):
    agent: ArgAgent

    async def on_start(self):
        logger.info("{}: Entering EnterState")

    async def run(self):
        msg = await self.receive(timeout=MSG_TIMEOUT)
        if msg:
            enter_dialogue = self.agent.do_enter_dialogue(msg)
            await self.send(msg)
            if enter_dialogue:
                self.next_state(PROPOSE_STATE)
            else:
                self.next_state(OPEN_STATE)


class DieState(State):
    agent: ArgAgent

    async def on_start(self):
        logger.info("{}: Entering DieState")

    async def run(self):
        msg = await self.receive(timeout=MSG_TIMEOUT)
        if msg:
            self.agent.do_die()


class ProposeState(State):
    agent: ArgAgent

    async def on_start(self):
        logger.info("{}: Entering ProposeState")

    async def run(self):
        msg = await self.receive(timeout=MSG_TIMEOUT)
        if msg:
            propose = self.agent.do_propose(msg)
            await self.send(msg)
            if propose:
                self.next_state(CENTRAL_STATE)
            else:
                self.next_state(OPEN_STATE)


class CentralState(State):
    agent: ArgAgent

    async def on_start(self):
        logger.info("{}: Entering CentralState")

    async def run(self):
        msg = await self.receive(timeout=int(random() * MSG_TIMEOUT))
        if msg:
            performative = msg.get_metadata(PERFORMATIVE)
            if performative == WHY_PERF:
                self.agent.current_why_agent_id = msg.sender
                self.next_state(ASSERT_STATE)
            elif performative == FINISH_DIALOGUE_PERF:
                self.agent.finish_dialogue()
                self.next_state(SEND_POSITION_STATE)
            elif performative == ACCEPTS_PERF:
                self.agent.do_my_position_accepted(msg)
                self.next_state(CENTRAL_STATE)
        else:
            self.next_state(CENTRAL_STATE)


class AssertState(State):
    agent: ArgAgent

    async def on_start(self):
        logger.info("{}: Entering AssertState")

    async def run(self):
        msg = await self.receive(timeout=MSG_TIMEOUT)
        if msg:
            asserts = self.agent.do_assert(msg, self.agent.current_why_agent_id)
            await self.send(msg)
            if asserts == ASSERT_PERF:
                self.next_state(WAIT_ATTACK_STATE)
            elif asserts == NO_COMMIT_PERF:
                self.agent.do_no_commit(msg)
                self.next_state(PROPOSE_STATE)
            else:
                self.next_state(CENTRAL_STATE)


class WaitAttackState(State):
    agent: ArgAgent

    async def on_start(self):
        logger.info("{}: Entering WaitAttackState")

    async def run(self):
        msg = await self.receive(timeout=MSG_TIMEOUT)
        if msg:
            performative = msg.get_metadata(PERFORMATIVE)
            if performative == ACCEPTS_PERF:
                self.agent.do_my_position_accepted(msg)
                self.next_state(CENTRAL_STATE)
            elif performative == ATTACKS_PERF:
                self.next_state(DEFEND_STATE)
            else:
                self.next_state(CENTRAL_STATE)


class DefendState(State):
    agent: ArgAgent

    async def on_start(self):
        logger.info("{}: Entering DefendState")

    async def run(self):
        msg = await self.receive(timeout=MSG_TIMEOUT)
        if msg:
            msg_to_send = ArgMessage()
            attack = self.agent.do_attack(msg_to_send, msg, True)
            if attack:
                self.next_state(WAIT_ATTACK_STATE)
            else:
                self.agent.do_no_commit(msg)
                self.next_state(PROPOSE_STATE)


class QueryPositionsState(State):
    agent: ArgAgent

    async def on_start(self):
        logger.info("{}: Entering QueryPositionsState")

    async def run(self):
        msg = await self.receive(timeout=MSG_TIMEOUT)
        if msg:
            msg_to_send = ArgMessage()
            self.agent.do_query_positions(msg_to_send)
            await self.send(msg_to_send)
            self.next_state(GET_POSITIONS_STATE)  # TODO more doubts with the wait states


class SendPositionState(State):
    agent: ArgAgent

    async def on_start(self):
        logger.info("{}: Entering SendPositionState")

    async def run(self):
        msg = await self.receive(timeout=MSG_TIMEOUT)
        if msg:  # TODO is this necessary? The content of the message seems irrelevant
            self.agent.do_send_position(msg)
            await self.send(msg)
            self.next_state(SOLUTION_STATE)


class SolutionState(State):
    agent: ArgAgent

    async def on_start(self):
        logger.info("{}: Entering SolutionState")

    async def run(self):
        msg = await self.receive(timeout=MSG_TIMEOUT)
        if msg:
            self.agent.do_solution(msg)
            await self.send(msg)
            self.next_state(OPEN_STATE)


class GetPositionsState(State):
    agent: ArgAgent

    async def on_start(self):
        logger.info("{}: Entering GetPositionsState")

    async def run(self):
        msg = await self.receive(timeout=MSG_TIMEOUT)
        if msg:
            performative = msg.get_metadata(PERFORMATIVE)
            if performative == FINISH_DIALOGUE_PERF:
                self.next_state(SEND_POSITION_STATE)
            elif performative == GET_ALL_POSITIONS_PERF:
                self.agent.do_get_positions(msg)
            else:
                self.next_state(CENTRAL_STATE)


class WhyState(State):
    agent: ArgAgent

    async def on_start(self):
        logger.info("{}: Entering WhyState")

    async def run(self):
        msg = await self.receive(timeout=MSG_TIMEOUT)
        if msg:
            why = self.agent.do_why(msg)
            if why:
                self.next_state(WAIT_ASSERT_STATE)
            else:
                self.next_state(CENTRAL_STATE)


class WaitAssertState(State):
    agent: ArgAgent

    async def on_start(self):
        logger.info("{}: Entering WaitAssertState")

    async def run(self):
        msg = await self.receive(timeout=MSG_TIMEOUT)
        if msg:
            performative = msg.get_metadata(PERFORMATIVE)
            if performative == ASSERTS_PERF:
                self.next_state(ATTACK_PERF)
            elif performative == NO_COMMIT_PERF:
                self.next_state(CENTRAL_STATE)
            else:
                self.next_state(CENTRAL_STATE)


class AttackState(State):
    agent: ArgAgent

    async def on_start(self):
        logger.info("{}: Entering AttackState")

    async def run(self):
        msg = await self.receive(timeout=MSG_TIMEOUT)
        if msg:
            msg_to_send = ArgMessage()
            attack = self.agent.do_attack(msg_to_send, msg, False)
            if attack:
                self.next_state(ATTACK2_STATE)
            else:
                self.agent.do_no_commit(msg)
                self.next_state(CENTRAL_STATE)


class Attack2State(State):
    agent: ArgAgent

    async def on_start(self):
        logger.info("{}: Entering Attack2State")

    async def run(self):
        msg = await self.receive(timeout=MSG_TIMEOUT)
        if msg:
            performative = msg.get_metadata(PERFORMATIVE)
            if performative == ATTACKS_PERF:
                self.next_state(ATTACK_STATE)
            elif performative == NO_COMMIT_PERF:
                self.agent.do_other_no_commit(msg)
                self.next_state(CENTRAL_STATE)
            else:
                self.next_state(CENTRAL_STATE)
