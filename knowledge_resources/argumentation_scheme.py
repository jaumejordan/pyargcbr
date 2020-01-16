from dataclasses import dataclass, field

from knowledge_resources.author import Author
from knowledge_resources.conclusion import Conclusion
from knowledge_resources.premise import Premise


@dataclass
class ArgumentationScheme:
    id: int = -1
    concluision: Conclusion = Conclusion()
    arg_title: str = ""
    creation_date: str = ""
    author: Author = Author()
    premises: list = field(default=[])
    presumptions: list = field(default=[])
    exceptions: list = field(default=[])

    def remove_premise(self, old_premise: Premise):
        self.premises.remove(old_premise)

    def remove_exception(self, old_exception: Premise):
        self.exceptions.remove(old_exception)

    def remove_presumption(self, old_presumption: Premise):
        self.presumptions.remove(old_presumption)

    def add_premise(self, new_premise: Premise):
        self.premises.append(new_premise)

    def add_exception(self, new_exception: Premise):
        self.exceptions.append(new_exception)

    def add_presumption(self, new_presumption: Premise):
        self.presumptions.append(new_presumption)



