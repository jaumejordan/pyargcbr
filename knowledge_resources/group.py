from typing import List
from knowledge_resources.social_entity import SocialEntity
from dataclasses import dataclass, field


@dataclass
class Group(SocialEntity):
    """Implementation of the concept Group"""
    agents: List[SocialEntity] = field(default_factory=lambda:[])

    def remove_member(self, old_member: SocialEntity):
        """Removes a member from the agents list (agents)

        Args:
            old_member (SocialEntity): The member that will be removed
        """
        self.agents.remove(old_member)

    def add_member(self, new_member: SocialEntity):
        """Adds a member to the agents list (agents)

        Args:
            new_member (SocialEntity): The member that will be added
        """
        self.agents.append(new_member)
