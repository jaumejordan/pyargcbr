from dataclasses import dataclass
from enum import Enum


@dataclass
class Server:
    host: str = "0.0.0.0"
    port: int = 0000
    name: str = "localhost"
    database: str = "arg_cbr"
    user: str = "root"
    password: str = "1234"


class SimilarityType(Enum):
    NORMALIZED_EUCLIDEAN = 0
    WEIGHTED_EUCLIDEAN = 1
    NORMALIZED_TVERSKY = 2


@dataclass
class DomainCBR:
    similarity: SimilarityType = SimilarityType.NORMALIZED_EUCLIDEAN


@dataclass
class ArgCbr:
    opponent_id_weight: int = 1
    proponent_pref_weight: int = 1
    proponent_id_weight: int = 1
    opponent_pref_weight: int = 1
    group_id_weight: int = 1
    group_pref_weight: int = 1
