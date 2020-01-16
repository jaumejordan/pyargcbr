from knowledge_resources.social_entity import SocialEntity
from dataclasses import dataclass, field


@dataclass
class Group(SocialEntity):
    # SocialEntity
    agents: list = field(default=[])

    def remove_member(self, old_member: SocialEntity):
        self.agents.remove(old_member)

    def add_member(self, new_member: SocialEntity):
        self.agents.append(new_member)
