from typing import List
from knowledge_resources.social_entity import SocialEntity
from dataclasses import dataclass, field


@dataclass
class Group(SocialEntity):
    agents: List[SocialEntity] = field(default=[])

    def remove_member(self, old_member: SocialEntity):
        self.agents.remove(old_member)

    def add_member(self, new_member: SocialEntity):
        self.agents.append(new_member)
