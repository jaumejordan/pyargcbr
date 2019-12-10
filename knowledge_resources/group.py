from knowledge_resources.social_entity import SocialEntity
from dataclasses import dataclass, field


@dataclass
class Group(SocialEntity):
    agents: list[SocialEntity] = field(default=SocialEntity())

    def remove_member(self, old_member: SocialEntity):
        self.agents.remove(old_member)
