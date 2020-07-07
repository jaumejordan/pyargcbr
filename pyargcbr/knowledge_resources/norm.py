from dataclasses import dataclass


@dataclass
class Norm:
    """Implementation of the concept Norm

    In this version of the API, Norms are not considered, but this class can
    be used to include normative knowledge in further implementations.
    """
    id: int = -1
    description: str = ""
