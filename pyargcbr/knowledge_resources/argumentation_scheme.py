from dataclasses import dataclass, field

from .author import Author
from .conclusion import Conclusion
from .premise import Premise


@dataclass
class ArgumentationScheme:
    """In this version of the API, Argumentation-Schemes are not considered, but
    this class can be used to include general knowledge in further
    implementations.
    """
    id: int = -1
    concluision: Conclusion = Conclusion()
    arg_title: str = ""
    creation_date: str = ""
    author: Author = Author()
    premises: list = field(default_factory=lambda: [])
    presumptions: list = field(default_factory=lambda: [])
    exceptions: list = field(default_factory=lambda: [])

    def remove_premise(self, old_premise: Premise):
        """Removes a premise from the premises list (premises)

        Args:
            old_premise (Premise): The premise that will be removed
        """
        self.premises.remove(old_premise)

    def remove_exception(self, old_exception: Premise):
        """Removes a premise from the exceptions list (exceptions)

        Args:
            old_exception (Premise): The premise that will be removed
        """
        self.exceptions.remove(old_exception)

    def remove_presumption(self, old_presumption: Premise):
        """Removes a premise from the presumptions list (presumptions)

        Args:
            old_presumption (Premise): The premise that will be removed
        """
        self.presumptions.remove(old_presumption)

    def add_premise(self, new_premise: Premise):
        """Adds a premise to the premises list (premises)

        Args:
            new_premise (Premise): The premise that will be added
        """
        self.premises.append(new_premise)

    def add_exception(self, new_exception: Premise):
        """Adds a premise to the exceptions list (exceptions)

        Args:
            new_exception (Premise): The premise that will be added
        """
        self.exceptions.append(new_exception)

    def add_presumption(self, new_presumption: Premise):
        """Adds a premise to the presumptions list (presumptions)

        Args:
            new_presumption (Premise): The premise that will be added
        """
        self.presumptions.append(new_presumption)
