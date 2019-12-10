from dataclasses import dataclass, field

from knowledge_resources.argumentation_scheme import ArgumentationScheme
from knowledge_resources.justification import Justification


@dataclass
class ArgumentJustification(Justification):
    domain_cases_ids: list(int) = field(default=[])
    argument_cases_ids: list(int) = field(default=[])
    schemes: ArgumentationScheme = field(default=ArgumentationScheme())

