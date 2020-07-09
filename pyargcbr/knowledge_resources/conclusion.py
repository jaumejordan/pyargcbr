from dataclasses import dataclass


@dataclass
class Conclusion:
    """Implementation of the concept Conclusion"""
    id: int = 1
    description: str = ""
    # It's a dataclass, so we don't need to override __eq__
