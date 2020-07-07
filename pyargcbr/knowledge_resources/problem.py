from dataclasses import dataclass

from .domain_context import DomainContext


@dataclass
class Problem:
    """Implementation of the concept Problem

    Problem is a specialization of CaseComponent
    """
    context: DomainContext = DomainContext()
