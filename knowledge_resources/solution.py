from dataclasses import dataclass, field

from knowledge_resources.case_component import CaseComponent
from knowledge_resources.conclusion import Conclusion


@dataclass
class Solution(CaseComponent):
    """Implementation of the concept Solution"""
    conclusion: Conclusion = Conclusion()
    value: str = ""
    times_used: int = 0
