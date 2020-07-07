from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from .group import Group
from .social_entity import SocialEntity


class DependencyRelation(Enum):
    """Different types of dependency relations considered"""
    POWER = 1
    AUTHORISATION = 2
    CHARITY = 3


@dataclass
class SocialContext:
    """Implementation of the concept SocialContext

    SocialContext is a specialization of Context
    """
    proponent: Optional[SocialEntity] = field(default=SocialEntity())
    opponent: Optional[SocialEntity] = field(default=SocialEntity())
    group: Optional[Group] = field(default=Group())
    relation: Optional[DependencyRelation] = DependencyRelation.CHARITY
