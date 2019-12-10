from dataclasses import dataclass

from knowledge_resources.dommain_case import DomainCase
from knowledge_resources.premise import Premise


@dataclass
class SupportSet:
    premises = list[Premise] = []
    domain_cases = list[DomainCase]
    
