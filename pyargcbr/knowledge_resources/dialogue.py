from dataclasses import dataclass
from typing import List

from .problem import Problem


@dataclass
class Dialogue:
    """Implementation of the concept Dialogue"""
    dialogue_id: str
    agent_ids = List[str]
    problem: Problem

    def remove_agent_ids(self, agent_id: str) -> bool:
        """Removes an ID from the agent IDs list (agent_ids)

        Args:
            agent_id (str): The ID that will be removed

        Returns:
            bool: True if the ID is removed, False otherwise
        """
        if agent_id in self.agent_ids:
            self.agent_ids.remove(agent_id)
            return True
        else:
            return False

    def add_agent_ids(self, agent_id: str) -> bool:
        """Adds an ID to the agent IDs list (agent_ids)

        Args:
            agent_id (str): The ID that will be added

        Returns:
            bool: True if the ID is added, False otherwise
        """
        if agent_id in self.agent_ids:
            return False
        self.agent_ids.append(agent_id)
        return True
