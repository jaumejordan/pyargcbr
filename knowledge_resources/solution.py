from dataclasses import dataclass, field

from knowledge_resources.case_component import CaseComponent
from knowledge_resources.conclusion import Conclusion


@dataclass
class Solution(CaseComponent):
    conclusion: Conclusion = Conclusion()
    value: str = ""
    timesUsed: int = 0
