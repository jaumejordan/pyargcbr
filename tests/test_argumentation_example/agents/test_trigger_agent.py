from time import sleep
from datetime import datetime
from typing import List, Optional, Dict

from loguru import logger
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message

from pyargcbr.agents.arg_message import ArgMessage, create_message

from pyargcbr.agents.argumentation_agent import ArgAgent
from pyargcbr.agents.protocol import ADD_DIALOGUE_PERF, LAST_MODIFICATION_DATE_PERF, MSG_TIMEOUT, MessageCodification, \
    FINISH_DIALOGUE_PERF, GET_ALL_POSITIONS_PERF, SOLUTION_PERF, DIE_PERF
from pyargcbr.knowledge_resources.dialogue import Dialogue
from pyargcbr.knowledge_resources.domain_case import DomainCase
from pyargcbr.knowledge_resources.position import Position
from pyargcbr.knowledge_resources.social_entity import SocialEntity
from pyargcbr.knowledge_resources.solution import Solution


class TestTriggerAgent(Agent):
    """This class represents a tester agent in charge of sending the test domain-case to solve to a group
    of agents and acts as the initiator of the dialogue

    """

    def __init__(self, jid: str, password: str, social_entities: List[SocialEntity], commitment_store_id: str,
                 finish_filename: str, domain_cases: List[DomainCase], agents: List[ArgAgent],
                 multiplier_time_factor: int = 10, verify_security: bool = False):
        super().__init__(jid, password, verify_security)
        logger.info("{}: TestTriggerAgent created")

        self.my_id = jid
        self.social_entities = social_entities
        self.commitment_store_id = commitment_store_id
        self.finish_filename = finish_filename
        self.domain_cases = domain_cases
        self.agents = agents

        self.dialogue_init_time = 0
        self.multiplier_time_factor = multiplier_time_factor

    def finalize(self):  # TODO
        pass


class TestTriggerBehaviour(CyclicBehaviour):
    agent: TestTriggerAgent

    async def send(self, msg: ArgMessage):
        for receiver in msg.to:  # TODO Is this the way to do it?
            await super().send(Message(to=receiver, sender=msg.sender, metadata=msg.metadata, body=msg.body))

    def __init__(self):
        super().__init__()

    async def on_start(self):
        logger.info("Starting TestTriggerBehaviour of {}".format(self.agent.my_id))

    async def run(self):
        # TODO: The (sleep) times should be checked
        # Create the file where the results will be stored
        try:
            open(self.agent.finish_filename, "xb")
        except (FileExistsError, FileNotFoundError) as e:
            logger.exception("ERROR CREATING FINISH FILE:\n{}".format(e))
        # Waits 2 seconds at the beginning to let the other agent get full started
        try:
            sleep(2)
        except (InterruptedError, KeyboardInterrupt) as e:
            logger.exception("TestTriggerBehaviour interrupted during waiting time:\n{}".format(e))

        # create a new instance of the domain-case without the solutions, to act as a new problem to solve
        n_domain_case = 0
        aux_domain_case = self.agent.domain_cases[n_domain_case]
        domain_case2send = aux_domain_case

        # The dialogue that will represent the tested conversation
        time = datetime.now().microsecond
        current_dialogue_id = str(time)
        agent_ids: List[str] = []
        dialogue = Dialogue(dialogue_id=current_dialogue_id, agent_ids=agent_ids,
                            problem=domain_case2send.problem)

        # Store the initial date of the dialogue
        dialogue_init_time = datetime.now().microsecond

        # Store the initial date of dialogue and send it to the commitment store so it can be added
        self.agent.dialogue_init_time = datetime.now().microsecond
        add_dialogue_msg = create_message(self.agent.my_id, self.agent.commitment_store_id, self.agent.name,
                                          self.agent.commitment_store_id, ADD_DIALOGUE_PERF, current_dialogue_id, None)
        await self.send(add_dialogue_msg)
        # Broadcast the dialogue opening
        entities_ids = [entity.name for entity in self.agent.social_entities]
        open_dialogue_msg = create_message(self.agent.my_id, self.agent.commitment_store_id, self.agent.name,
                                           entities_ids, ADD_DIALOGUE_PERF, current_dialogue_id, None)
        await self.send(open_dialogue_msg)
        n_domain_case += 1

        final_solution = Solution()
        win_position_agents: Optional[str] = None

        # MAIN LOOP OPENING
        while True:
            # For multiplier_time_factor == 1 the wait between iterations equals a tenth of a second
            sleep(0.1 * self.agent.multiplier_time_factor)

            # Ask to commitment store the elapsed milliseconds since the last modification
            # (check if there are new arguments or positions)
            elapsed_time_msg = create_message(self.agent.my_id, self.agent.commitment_store_id, self.agent.name,
                                              self.agent.commitment_store_id, LAST_MODIFICATION_DATE_PERF,
                                              current_dialogue_id, None)
            await self.send(elapsed_time_msg)

            msg = await self.receive(timeout=MSG_TIMEOUT)
            if not msg:
                logger.error("{}: Commitment Store does not respond!!!".format(self.agent.name))
                continue
            millis_of_difference: int = MessageCodification.get_decoded_message_content(msg)
            logger.info("{}: millis difference= {}".format(self.agent.name, millis_of_difference))

            # Shall the dialogue be stopped?
            if millis_of_difference > 150 * self.agent.multiplier_time_factor:
                # More than one iteration time has passed without updates -> It must end
                logger.info("DIALOGUE MUST FINISH!\n".format(self.agent.name))

                # Broadcast the decision
                finnish_dialogue_msg = create_message(self.agent.my_id, self.agent.commitment_store_id, self.agent.name,
                                                      entities_ids, FINISH_DIALOGUE_PERF, current_dialogue_id, None)
                await self.send(finnish_dialogue_msg)

                # Wait to give time to the agents to send their position
                # (with the timesAccepted updated) to the Commitment Store
                try:
                    sleep(0.025 * self.agent.multiplier_time_factor)
                except (InterruptedError, KeyboardInterrupt) as e:
                    logger.exception(e)

                # Select the most frequent position (or the most voted in case of draw). Make a random choice otherwise
                all_positions = self.get_all_positions(current_dialogue_id)
                possible_solutions: Dict[int, Solution] = dict()
                frequent_positions: Dict[int, int] = dict()
                voted_positions: Dict[int, int] = dict()
                positions_per_solution: Dict[int, List[Position]] = dict()
                for pos in all_positions:
                    sol_id = pos.solution.conclusion.id
                    sol = possible_solutions.get(sol_id, None)
                    if sol:  # Solution already considered as a possibility
                        # Increase the frequency value for the solution
                        frequent_positions[sol_id] += 1
                        # Sum the votes
                        voted_positions[sol_id] += pos.times_accepted
                        # Add this position to the other positions defending the same solution
                        positions_per_solution[sol_id].append(pos)
                    else:  # Solution not yet considered as a possibility
                        possible_solutions[sol_id] = sol
                        frequent_positions[sol_id] = 1
                        voted_positions[sol_id] = pos.times_accepted
                        positions_per_solution[sol_id] = [pos]

                # Obtain the most voted position TODO: Potentially improvable implementation; Not urgent
                sorted_votes: Dict[int, int] = {k: v for k, v in sorted(voted_positions.items(),
                                                                        key=lambda item: item[1], reverse=True)}
                draw_solutions: List[int] = []
                max_voted = None
                max_votes = -1
                for sol_id in sorted_votes.keys():
                    if not max_voted:
                        max_voted = sol_id
                        max_votes = sorted_votes[sol_id]
                        continue
                    sol_votes = sorted_votes[sol_id]
                    if sol_votes < max_votes:
                        break
                    elif draw_solutions:
                        draw_solutions.append(sol_id)
                    else:
                        draw_solutions = [max_voted, sol_id]

                final_solution: Optional[Solution] = None
                # If there is not draw in voted positions, take the most voted position as the final solution
                if not draw_solutions:
                    final_solution = possible_solutions[max_voted]
                # If there is a draw in voted positions, obtain the most frequent position
                # If there is again draw, take the position with bigger index of the most frequent positions
                else:
                    sorted_frequencies: Dict[int, int] = {k: v for k, v in sorted(frequent_positions.items(),
                                                          key=lambda item: item[1], reverse=True)}
                    draw_frequencies: List[int] = []
                    max_frequent = None
                    max_frequency = -1
                    for sol_id in sorted_frequencies.keys():
                        if not max_frequent:
                            max_frequent = sol_id
                            max_frequency = sorted_votes[sol_id]
                            continue
                        sol_frequency = sorted_votes[sol_id]
                        if sol_frequency < max_frequency:
                            break
                        elif draw_solutions:
                            draw_frequencies.append(sol_id)
                        else:
                            draw_frequencies = [max_frequent, sol_id]

                    if not draw_frequencies:
                        final_solution = possible_solutions[max_frequent]
                    else:
                        max_sol_id = max(draw_frequencies)
                        final_solution = possible_solutions[max_sol_id]

                if not final_solution:
                    final_solution = Solution()
                    win_position_agents = ""
                if final_solution.conclusion.id != -1:  # -1 is the default value
                    # To print the agent_ids that proposed each position
                    positions = positions_per_solution[final_solution.conclusion.id]
                    agent_ids2 = " ".join([pos.agent_id for pos in positions])
                    win_positions_agents = "[{}]".format(agent_ids2)
                    logger.info("\n{}\nFINAL SOLUTION:\n solutionID={} promoted_value={} times_used={}"
                                " proposing_agents={} frequency={} votes={}".
                                format("+"*20, final_solution.conclusion.id, final_solution.value,
                                       final_solution.times_used, agent_ids2,
                                       frequent_positions[final_solution.conclusion.id],
                                       voted_positions[final_solution.conclusion.id]))
                    dialogue_time = datetime.now().microsecond - dialogue_init_time
                    logger.info("Dialogue elapsed time: {:3f} seconds".format(dialogue_time / 1000))
                    pos_sols_str = "POSSIBLE SOLUTIONS: \n"
                    for sol in possible_solutions:
                        sol: Solution
                        positions = positions_per_solution[sol.conclusion.id]
                        agent_ids2 = " ".join([pos.agent_id for pos in positions])
                        pos_sols_str += "solutionID={} promoted_value={} times_used={} " \
                                        "proposing_agents={} frequency={} votes={}\n".format(
                                           sol.conclusion.id, sol.value,
                                           sol.times_used, agent_ids2,
                                           frequent_positions[sol.conclusion.id],
                                           voted_positions[sol.conclusion.id])
                    pos_sols_str += "+" * 10 + "\n"
                    logger.info(pos_sols_str)

                # Send the solution to all agents, in case it's correct
                send_sol_msg = create_message(self.agent.my_id, self.agent.commitment_store_id, self.agent.name,
                                              entities_ids, SOLUTION_PERF, current_dialogue_id, None)
                await self.send(send_sol_msg)

                if final_solution.conclusion.id not in [0, -1]:
                    ticket_sent: DomainCase = self.agent.domain_cases[n_domain_case - 1]
                    ticket_solutions: List[Solution] = ticket_sent.solutions
                    org_solutions = " ".join([str(sol.conclusion.id) for sol in ticket_solutions])
                    logger.info("{0}: proposed_sol={1} by: {2} original_solutions={3} {0}".format(
                        "\n\n" + "*" * 10 + "\n", self.agent.name, final_solution.conclusion.id, org_solutions))
                else:  # NO SOLUTION
                    logger.info("{0}{1}:{0}".format("\n\n" + "*" * 10 + "\n", self.agent.name))

                break
        # MAIN LOOP CLOSURE
        # Wait to give time to agents to update its case-bases
        try:
            sleep(0.5)
        except (InterruptedError, KeyboardInterrupt) as e:
            logger.exception(e)

        # Put them to rest :D
        stop_msg = create_message(self.agent.my_id, self.agent.commitment_store_id, self.agent.name,
                                  entities_ids + [self.agent.commitment_store_id], DIE_PERF, current_dialogue_id, None)
        await self.send(stop_msg)
        # Wait until all agents are finished
        try:
            sleep(1)
        except (InterruptedError, KeyboardInterrupt) as e:
            logger.exception(e)

        try:
            # Create file
            with open(self.agent.finish_filename, "wt") as f:
                f.write("Test finished\n")
        except FileNotFoundError as e:
            logger.exception(e)

    def get_all_positions(self, dialogue_id: str) -> List[Position]:
        get_pos_msg = create_message(self.agent.my_id, self.agent.commitment_store_id, self.agent.name,
                                     self.agent.commitment_store_id, GET_ALL_POSITIONS_PERF, dialogue_id, None)
        await self.send(get_pos_msg)
        msg_res = await self.receive(timeout=MSG_TIMEOUT)
        if not msg_res:
            logger.error("{}: FATAL ERROR - Commitment Store does not respond!!! Cannot get the positions".
                         format(self.agent.name))
            return []
        positions: List[Position] = MessageCodification.get_decoded_message_content(msg_res)
        return positions
