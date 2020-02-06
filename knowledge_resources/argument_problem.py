from dataclasses import dataclass, field
from knowledge_resources.problem import Problem
from knowledge_resources.social_context import SocialContext


@dataclass
class ArgumentProblem(Problem):
    social_context: SocialContext = field(default=SocialContext())
