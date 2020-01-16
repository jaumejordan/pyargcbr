from dataclasses import dataclass, field

from knowledge_resources.case_component import CaseComponent
from knowledge_resources.domain_context import DomainContext


@dataclass
class Problem(CaseComponent):
    context: DomainContext = DomainContext()
