from dataclasses import dataclass, field

from .problem import Problem
from .social_context import SocialContext


@dataclass
class ArgumentProblem(Problem):
    """Implementation of the concept ArgumentProblem"""
    social_context: SocialContext = field(default=SocialContext())
