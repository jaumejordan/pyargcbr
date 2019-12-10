from dataclasses import dataclass, field
from knowledge_resources.domain_context import DomainContext


@dataclass
class Problem:
    context: DomainContext = field(default=DomainContext())
