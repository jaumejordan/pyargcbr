from dataclasses import dataclass


@dataclass
class Case:
    id: int = -1
    # TODO Maybe using datetime is a better idea -> It is not necessary (see metrics.py)
    creation_date: str = ""
