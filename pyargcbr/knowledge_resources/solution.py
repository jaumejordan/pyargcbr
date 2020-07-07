from dataclasses import dataclass

from .conclusion import Conclusion


@dataclass
class Solution:
    """Implementation of the concept Solution"""
    conclusion: Conclusion = Conclusion()
    value: str = ""
    times_used: int = 0
