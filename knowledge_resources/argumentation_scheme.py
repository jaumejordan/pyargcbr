from dataclasses import dataclass, field

from knowledge_resources.author import Author
from knowledge_resources.premise import Premise


@dataclass
class ArgumentationScheme:
    id: int = -1
    arg_title: str = ""
    creation_date: str = ""
    author: Author = field(default=Author())
    premises: list[Premise] = field(default=[])
    presumptions: list[Premise] = field(default=[])
    exceptions: list[Premise] = field(default=[])

    def remove_(self, old_premise: Premise):
        self.premises.remove(old_premise)

    def remove_(self, old_exception: Premise):
        self.exceptions.remove(old_exception)

    def remove_(self, old_presumption: Premise):
        self.presumptions.remove(old_presumption)



