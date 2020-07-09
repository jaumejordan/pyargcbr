from dataclasses import dataclass

import pyargcbr.configuration.settings as settings
from ..configuration.configuration_parameters import SimilarityType


@dataclass
class Configuration:
    server_name: str = settings.Server.name
    database_name: str = settings.Server.database
    user_name: str = settings.Server.user
    password: str = settings.Server.password
    domain_cbrs_similarity: SimilarityType = settings.DomainCBR.similarity
    arg_cbr_proponent_id_weight: float = settings.ArgCbr.proponent_id_weight
    arg_cbr_proponent_pref_weight: float = settings.ArgCbr.proponent_pref_weight
    arg_cbr_opponent_id_weight: float = settings.ArgCbr.opponent_id_weight
    arg_cbr_opponent_pref_weight: float = settings.ArgCbr.opponent_pref_weight
    arg_cbr_group_id_weight: float = settings.ArgCbr.group_id_weight
    arg_cbr_group_pref_weight: float = settings.ArgCbr.group_pref_weight
