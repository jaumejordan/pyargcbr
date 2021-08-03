from random import randint
from typing import List, Tuple, Set, Union, Optional
from itertools import permutations

from loguru import logger

from pyargcbr.agents.argumentation_agent import ArgAgent
from pyargcbr.knowledge_resources.group import Group
from pyargcbr.knowledge_resources.social_context import DependencyRelation
from pyargcbr.knowledge_resources.social_entity import SocialEntity
from pyargcbr.knowledge_resources.valpref import ValPref

"""This file has different methods to create groups of agents and some of their parameters
NOTE: The original Java code represented this as a class with all static methods. This format
here is used because we consider it more appropriate for a Python project

"""


def get_valpref_list(values: Tuple[str] = ("savings", "quality", "speed")) -> List[ValPref]:
    """Gets a Tuple of str representing the values and returns a list of ValPref
    result of the permutation of these values

    Args:
        values (Tuple[str]): All the preferred values to be permuted. By default
            these are: "savings", "quality" and "speed"

    Returns:
        List[ValPref]: The resultant List of ValPref
    """
    value_permutations = permutations(values)
    preferred_values: List[ValPref] = [ValPref(values=list(perm)) for perm in value_permutations]
    return preferred_values


def get_valpref_void_list() -> List[ValPref]:
    """Returns a List of ValPref with void preference

    Returns:
        List[ValPref]: The resultant List of ValPref with void preference
    """
    return get_valpref_list(values=tuple(""))


def create_empty_argument_cases_partitions(dest_file_names: Union[Set[str], List[str]],
                                           check_existing_files: bool = False) -> None:
    """Creates a series of files to represent partitions of argument-cases

    Args:
        dest_file_names (Union[Set[str], List[str]]): The names of the files
            used to store the partitions
        check_existing_files (bool): If set to true checks if the files already
            exist. Logs an error in that case
    """
    if type(dest_file_names) == list:
        dest_file_names = set(dest_file_names)

    for file in dest_file_names:
        try:
            if check_existing_files:
                open(file, "xb")
                continue
            with open(file, "wb") as f:  # This should clean the file
                pass
        except (FileNotFoundError, FileExistsError) as e:
            logger.exception(e)


def create_social_entities(base_name: str, n_operators: int, n_experts: int,
                           n_managers: int, values: Optional[Tuple[str]] = None,
                           valpref: Optional[Tuple[str]] = None,
                           dif_roles: bool = False) -> List[SocialEntity]:
    """Creates a List of SocialEntities with the given base name and the number
    of operators, experts and manager specified. The values passed will be used
    to establish the possible preferred values.

    # NOTE: The method has been adapted from the original Java code the
    reduce the number of methods required. In that code there were different
    methods for different orders of distributions for the SocialEntity in the
    List Changes in the implementation have to be carefully executed

    Args:
        base_name (str): Name to put as base of the SocialEntity
        n_operators (int): Amount of SocialEntity that are operators
        n_experts (int): Amount of SocialEntity that are experts
        n_managers (int): Amount of SocialEntity that are managers
        values (Optional[Tuple[str]]): Tuple of str used to establish the
            preferred values via permutation. If None the default values will be
            used ("savings", "quality" and "speed")
        valpref (Optional[Tuple[str]]): Default is None and implies that each
            SocialEntity gets its preferred values randomly. Otherwise all
            entities get assigned the ValPref derived from these
        dif_roles (bool): Determines the distribution of the SocialEntity
            [_False (default): Operators -> Experts -> Managers _True: Managers
            -> Experts -> Operators]

    Returns:
        List[SocialEntity]: The resultant List of SocialEntity
    """
    preferred_values: List[ValPref] = []
    if not valpref:
        if not values:
            get_valpref_list()
        else:
            get_valpref_list(values)
    else:
        preferred_values.append(ValPref(values=list(valpref)))

    social_entities: List[SocialEntity] = []
    operator_social_entities: List[SocialEntity] = []
    for i in range(n_operators):
        social_entity = SocialEntity(id=i,
                                     name=base_name + "Operator" + str(i),
                                     role="operator",
                                     norms=[],  # NOTE: In the original Java code this value was set to "null"
                                     # NOTE: In the original Java code the index was "1"
                                     # but it's not error-free withe this adaptation
                                     valpref=preferred_values[0])
        operator_social_entities.append(social_entity)
    expert_social_entities: List[SocialEntity] = []
    for i in range(n_experts):
        social_entity = SocialEntity(id=n_operators + i,  # NOTE: In the original Java code this value was set to "i"
                                     name=base_name + "Expert" + str(i),
                                     role="expert",
                                     norms=[],  # NOTE: IDEM
                                     valpref=preferred_values[0])  # NOTE: IDEM
        expert_social_entities.append(social_entity)
    manager_social_entities: List[SocialEntity] = []
    for i in range(n_managers):
        social_entity = SocialEntity(id=n_operators + n_experts + i,  # NOTE: IDEM
                                     name=base_name + "Manager" + str(i),
                                     role="manager",
                                     norms=[],  # NOTE: IDEM
                                     valpref=preferred_values[0])  # NOTE: IDEM
        manager_social_entities.append(social_entity)

    if dif_roles:
        social_entities = manager_social_entities + expert_social_entities + operator_social_entities
    else:
        social_entities = operator_social_entities + expert_social_entities + manager_social_entities
    return social_entities


def create_social_entities_void_values(base_name: str, n_operators: int, n_experts: int,
                                       n_managers: int, values: Optional[Tuple[str]] = None,
                                       dif_roles: bool = True) -> List[SocialEntity]:
    """Creates a List of SocialEntities with void values, the given base name
    and the number of operators, experts and manager specified. The values
    passed will be used to establish the possible other preferred values.

    # NOTE: The method has been adapted from the original Java code the
    reduce the number of methods required. Changes in the implementation have to
    be carefully executed.

    Args:
        base_name (str): Name to put as base of the SocialEntity
        n_operators (int): Amount of SocialEntity that are operators
        n_experts (int): Amount of SocialEntity that are experts
        n_managers (int): Amount of SocialEntity that are managers
        values (Optional[Tuple[str]]): Tuple of str used to establish the other
            preferred values via permutation. If None the default values will be
            used ("savings", "quality" and "speed")
        dif_roles (bool): Determines the distribution of the SocialEntity
            [_False: Operators -> Experts -> Managers _True (default): Managers
            -> Experts -> Operators]

    Returns:
        List[SocialEntity]: The resultant List of SocialEntity
    """
    preferred_values: List[ValPref] = []
    if not values:
        get_valpref_list()
    else:
        get_valpref_list(values)
    preferred_values_void: List[ValPref] = get_valpref_void_list()
    social_entities: List[SocialEntity] = []

    num_valprefs = len(preferred_values_void)
    social_entity = SocialEntity()
    operator_social_entities: List[SocialEntity] = []
    for i in range(n_operators):
        index = randint(0, num_valprefs)
        if i == 0 and index < num_valprefs - 1:
            social_entity = SocialEntity(id=i,
                                         name=base_name + "Operator" + str(i), role="operator",
                                         norms=[],  # NOTE: In the original Java code this value was set to "null"
                                         valpref=preferred_values[index])
        elif i == 0:
            social_entity = SocialEntity(id=i,
                                         name=base_name + "Operator" + str(i), role="operator",
                                         norms=[],  # NOTE: IDEM
                                         valpref=preferred_values[num_valprefs - 1])
        else:
            social_entity = SocialEntity(id=i,
                                         name=base_name + "Operator" + str(i), role="operator",
                                         norms=[],  # NOTE: IDEM
                                         valpref=preferred_values[0])
        operator_social_entities.append(social_entity)

    expert_social_entities: List[SocialEntity] = []
    for i in range(n_experts):
        index = randint(0, num_valprefs)
        if i == 0 and index < num_valprefs - 1:
            social_entity = SocialEntity(id=n_operators + i,
                                         name=base_name + "Expert" + str(i), role="expert",
                                         norms=[],  # NOTE: In the original Java code this value was set to "null"
                                         valpref=preferred_values[index])
        elif i == 0:
            social_entity = SocialEntity(id=n_operators + i,
                                         name=base_name + "Expert" + str(i), role="expert",
                                         norms=[],  # NOTE: IDEM
                                         valpref=preferred_values[num_valprefs - 1])
        else:
            social_entity = SocialEntity(id=n_operators + i,
                                         name=base_name + "Expert" + str(i), role="expert",
                                         norms=[],  # NOTE: IDEM
                                         valpref=preferred_values[0])
        expert_social_entities.append(social_entity)

    manager_social_entities: List[SocialEntity] = []
    for i in range(n_managers):
        index = randint(0, num_valprefs)
        if i == 0 and index < num_valprefs - 1:
            social_entity = SocialEntity(id=n_operators + n_experts + i,
                                         name=base_name + "Manager" + str(i), role="manager",
                                         norms=[],  # NOTE: In the original Java code this value was set to "null"
                                         valpref=preferred_values[index])
        elif i == 0:
            social_entity = SocialEntity(id=n_operators + i,
                                         name=base_name + "Manager" + str(i), role="manager",
                                         norms=[],  # NOTE: IDEM
                                         valpref=preferred_values[num_valprefs - 1])
        else:
            social_entity = SocialEntity(id=n_operators + i,
                                         name=base_name + "Manager" + str(i), role="manager",
                                         norms=[],  # NOTE: IDEM
                                         valpref=preferred_values[0])
        social_entities.append(social_entity)

    if dif_roles:
        social_entities = manager_social_entities + expert_social_entities + operator_social_entities
    else:
        social_entities = operator_social_entities + expert_social_entities + manager_social_entities
    return social_entities


def create_friend_lists(social_entities: List[SocialEntity]) -> List[List[SocialEntity]]:
    """Creates a List for each SocialEntity given in the parameters. Each list
    in the results represents a list of friends for the corresponding agent
    (SocialEntity in input)

    Args:
        social_entities (List[SocialEntity]): List of SocialEntity to create the
            friend lists

    Returns:
        List[List[SocialEntity]]: The resultant List of List of SocialEntity
    """
    return [[friend for friend in social_entities if myself != friend]
            for myself in social_entities]


def create_dependency_relations(n_operators: int, n_experts: int, n_managers: int,
                                dif_roles: bool = False) -> List[List[DependencyRelation]]:
    """Creates a List with Lst of DependencyRelation for each operator, expert and manager specified

    Args:
        n_operators (int): Amount of SocialEntity that are operators
        n_experts (int): Amount of SocialEntity that are experts
        n_managers (int): Amount of SocialEntity that are managers
        dif_roles (bool): Determines the distribution of the List[DependencyRelation]
            [_False: Operators -> Experts -> Managers _True (default): Managers
            -> Experts -> Operators]

    Returns:
        List[List[DependencyRelation]]: The resulting List
    """
    # TODO: This is wrong almost 100%
    operator_dependency_relations = [DependencyRelation.CHARITY] * (n_operators - 1) + \
                                    [DependencyRelation.CHARITY] * n_experts + \
                                    [DependencyRelation.CHARITY] * n_managers
    expert_dependency_relations = [DependencyRelation.AUTHORISATION] * n_operators + \
                                  [DependencyRelation.CHARITY] * (n_experts - 1) + \
                                  [DependencyRelation.CHARITY] * n_managers
    manager_dependency_relations = [DependencyRelation.POWER] * n_operators + \
                                   [DependencyRelation.POWER] * n_experts + \
                                   [DependencyRelation.CHARITY] * (n_managers - 1)
    if dif_roles:
        return [manager_dependency_relations, expert_dependency_relations, operator_dependency_relations]
    return [operator_dependency_relations, expert_dependency_relations, manager_dependency_relations]


def create_dependency_relations_from_list(social_entities: List[SocialEntity]) -> List[List[DependencyRelation]]:
    """Creates a List with Lst of DependencyRelation for each operator, expert and manager specified

    Args:
        social_entities (List[SocialEntity]): The input is a List and the corresponding roles are
        extracted directly from the attributes of it elements

    Returns:
        List[List[DependencyRelation]]: The resulting List
    """
    dependency_relations: List[List[DependencyRelation]] = []
    for entity in social_entities:
        entity_dependency_relations: List[DependencyRelation] = []
        for other in social_entities:
            if other == entity:
                continue
            # NOTE: The following structure could be easily simplified, but it's been kept
            # like this for now because it's easy to handle
            if entity.role == "operator":
                if other.role == "operator":
                    entity_dependency_relations.append(DependencyRelation.CHARITY)
                elif other.role == "expert":
                    entity_dependency_relations.append(DependencyRelation.CHARITY)
                elif other.role == "manager":
                    entity_dependency_relations.append(DependencyRelation.CHARITY)
            elif entity.role == "expert":
                if other.role == "operator":
                    entity_dependency_relations.append(DependencyRelation.AUTHORISATION)
                elif other.role == "expert":
                    entity_dependency_relations.append(DependencyRelation.CHARITY)
                elif other.role == "manager":
                    entity_dependency_relations.append(DependencyRelation.CHARITY)
            elif entity.role == "manager":
                if other.role == "operator":
                    entity_dependency_relations.append(DependencyRelation.POWER)
                elif other.role == "expert":
                    entity_dependency_relations.append(DependencyRelation.POWER)
                elif other.role == "manager":
                    entity_dependency_relations.append(DependencyRelation.CHARITY)
        dependency_relations.append(entity_dependency_relations)
    return dependency_relations


def create_and_launch_argumentation_agents(social_entities: List[SocialEntity], friends_lists: List[List[SocialEntity]],
                                           dependency_relations: List[List[DependencyRelation]], group: Group,
                                           commitment_store_id: str,
                                           ini_domain_cases_file_path: List[str], fin_domain_cases_file_path: List[str],
                                           dom_cbr_index: int, dom_cbr_threshold: float,
                                           ini_arg_cases_file_path: List[str], fin_arg_cases_file_path: List[str],
                                           wpd: float = 1.0, wsd: float = 1.0, wrd: float = 1.0, wad: float = 1.0,
                                           wed: float = 1.0, wep: float = 1.0) -> List[ArgAgent]:
    agents: List[ArgAgent] = []
    for entity in social_entities:
        new_agent = ArgAgent(jid="qpid://" + entity.name + "@localhost:8000", password="password",
                             my_social_entity=entity, my_friends=friends_lists[entity.id],
                             dependency_relations=dependency_relations[entity.id], group=group,
                             commitment_store_id=commitment_store_id,
                             ini_domain_cases_file_path=ini_domain_cases_file_path[entity.id],
                             fin_domain_cases_file_path=fin_domain_cases_file_path[entity.id],
                             dom_cbr_index=dom_cbr_index, dom_cbr_threshold=dom_cbr_threshold,
                             ini_arg_cases_file_path=ini_arg_cases_file_path[entity.id],
                             fin_arg_cases_file_path=fin_arg_cases_file_path[entity.id],
                             wpd=wpd, wsd=wsd, wrd=wrd, wad=wad, wed=wed, wep=wep)
        await new_agent.start()
        agents.append(new_agent)
    return agents
