from dataclasses import dataclass
from knowledge_resources.acceptability_status import AcceptabilityStatus
from knowledge_resources.conclusion import Conclusion
from knowledge_resources.support_set import SupportSet

@dataclass
class Argument:
    id: int
    conclusion: Conclusion
    timesUsedConclusion: int
    value: str
    support_set: SupportSet
    acceptability_status: AcceptabilityStatus
    

