from dataclasses import dataclass


@dataclass
class Case:
    id: int = -1
    # TODO Maybe using datetime is a better idea
    creation_date: str = ""
