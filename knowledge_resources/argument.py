from dataclasses import dataclass, field

from knowledge_resources.acceptability_status import AcceptabilityStatus
from knowledge_resources.conclusion import Conclusion
from knowledge_resources.social_context import DependencyRelation
from knowledge_resources.support_set import SupportSet

@dataclass
class Argument:
    id: int = 1
    conclusion: Conclusion = Conclusion()
    times_used_conclusion: int = 0
    value: str = ""
    support_set: SupportSet = SupportSet()
    acceptability_state: AcceptabilityStatus = AcceptabilityStatus.UNDECIDED
    proponent_depen_relation: DependencyRelation = DependencyRelation()
    attacking_to_arg_id: int = -1
    received_attacks_counter_examples: list = field(default=[])
    received_attacks_dist_premises: list = field(default=[])

    def __str__(self):
        return "id=" + str(self.id) + "sol_id= " + str(self.conclusion.id) + str(self.conclusion.id) + \
            " promoted_value=" + self.value + " attacking_to_arg_id=" + str(self.attacking_to_arg_id) + \
            "\nSupport Set: " + str(self.support_set)

    def add_received_attacks_counter_examples(self, new_arg):
        self.received_attacks_counter_examples.append(new_arg)

    def add_received_attacks_dist_premises(self, new_arg):
        self.received_attacks_dist_premises.append(new_arg)
