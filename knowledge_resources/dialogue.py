from dataclasses import dataclass
from typing import List
from knowledge_resources.problem import Problem


@dataclass
class Dialogue:
    dialogue_id: str
    agent_ids = List[str]
    problem: Problem

    def remove_agent_ids(self, agent_id: str):
        if agent_id in self.agent_ids:
            self.agent_ids.remove(agent_id)
            return True
        else: return False

    def add_agent_ids(self, agent_id: str):
        if agent_id in self.agent_ids:
            return False
        self.agent_ids.append(agent_id)
        return True
