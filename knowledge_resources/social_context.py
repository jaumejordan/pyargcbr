from dataclasses import dataclass, field
from enum import Enum
from knowledge_resources.context import Context
from knowledge_resources.group import Group
from knowledge_resources.social_entity import SocialEntity


class DependencyRelation(Enum):
    """Different types of dependency relations considered"""
    POWER = 1
    AUTHORISATION = 2
    CHARITY = 3


@dataclass
class SocialContext(Context):
    """Implementation of the concept SocialContext

    SocialContext is a specialization of Context
    """
    proponent: SocialEntity = field(default=SocialEntity())
    opponent: SocialEntity = field(default=SocialEntity())
    group: Group = field(default=Group())
    relation: DependencyRelation = DependencyRelation.CHARITY
