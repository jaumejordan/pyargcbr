from dataclasses import dataclass, field

from knowledge_resources.conclusion import Conclusion


@dataclass
class Solution:
    conclusion: Conclusion = field(default=Conclusion())
    value: str = ""
    timesUsed: int = 0
