from typing import List, Set, Union, Dict
from random import randint
from pickle import load, dump
from loguru import logger

from pyargcbr.knowledge_resources.argument_case import ArgumentCase
from pyargcbr.knowledge_resources.domain_case import DomainCase

"""This file contains methods to create different partitions of domain-cases and argument-cases to make tests
NOTE: The original Java code represented this as a class with all static methods. This format
here is used because we consider it more appropriate for a Python project

"""


def create_domain_cases_partitions_incremental(n_cases: int, n_operators: int, cases_per_incremental: int = 5,
                                               original_filepath: str = "../resources/data/domain_cases/Helpdesk"
                                                                        "-DomainCases.dat",
                                               destination_dir_path: str = "partitionsInc/") -> None:
    """Creates the data files with the domain-cases serialized as Python Objects

    Args:
        n_cases (int): Amount of files to be created
        n_operators (int): Amount of operators
        cases_per_incremental (int): Amount of cases per partition
        original_filepath (str): Source file with all the domain-cases
        destination_dir_path (str): Directory where the partitions will be stored
    """
    create_cases_partitions_incremental(n_cases, n_operators, cases_per_incremental,
                                        original_filepath, destination_dir_path, DomainCase)


def create_argument_cases_partitions_incremental(n_cases: int, n_operators: int, cases_per_incremental: int = 5,
                                                 original_filepath: str = "../resources/data/argument_cases/test_cases"
                                                                          "_dom1_arg1.dat",
                                                 destination_dir_path: str = "partitionsArgInc/") -> None:
    """Creates the data files with the argument-cases serialized as Python Objects

    Args:
        n_cases (int): Amount of files to be created
        n_operators (int): Amount of operators
        cases_per_incremental (int): Amount of cases per partition
        original_filepath (str): Source file with all the argument-cases
        destination_dir_path (str): Directory where the partitions will be stored
    """
    create_cases_partitions_incremental(n_cases, n_operators, cases_per_incremental,
                                        original_filepath, destination_dir_path, ArgumentCase)


def create_domain_cases_partitions_continued(n_cases: int, n_operators: int, cases_per_incremental: int = 5,
                                             original_filepath: str = "../resources/data/domain_cases/Helpdesk"
                                                                      "-DomainCases.dat",
                                             destination_dir_path: str = "partitionsInc/") -> None:
    """Creates the data files with the domain-cases serialized as Python Objects

    Args:
        n_cases (int): Amount of files to be created
        n_operators (int): Amount of operators
        cases_per_incremental (int): Amount of EXTRA cases per partition
        original_filepath (str): Source file with all the domain-cases
        destination_dir_path (str): Directory where the partitions will be stored
    """
    create_cases_partitions_continued(n_cases, n_operators, cases_per_incremental,
                                      original_filepath, destination_dir_path, DomainCase)


def create_argument_cases_partitions_continued(n_cases: int, n_operators: int, cases_per_incremental: int = 5,
                                               original_filepath: str = "../resources/data/argument_cases/test_cases"
                                                                        "_dom1_arg1.dat",
                                               destination_dir_path: str = "partitionsArgInc/") -> None:
    """Creates the data files with the argument-cases serialized as Python Objects

    Args:
        n_cases (int): Amount of files to be created
        n_operators (int): Amount of operators
        cases_per_incremental (int): Amount of EXTRA cases per partition
        original_filepath (str): Source file with all the argument-cases
        destination_dir_path (str): Directory where the partitions will be stored
    """
    create_cases_partitions_continued(n_cases, n_operators, cases_per_incremental,
                                      original_filepath, destination_dir_path, ArgumentCase)


def create_cases_partitions_incremental(n_cases: int, n_operators: int, cases_per_incremental: int,
                                        original_filepath: str, destination_dir_path: str,
                                        case_type: type) -> None:
    """Auxiliary method; Creates the data files with the cases serialized as Python Objects

    Args:
        n_cases (int): Amount of files to be created
        n_operators (int): Amount of operators
        cases_per_incremental (int): Amount of cases per partition
        original_filepath (str): Source file with all the cases
        destination_dir_path (str): Directory where the partitions will be stored
        case_type (type): Only the loaded objects of this type will be stored
    """
    all_cases = read_cases_file(original_filepath)
    logger.info("Total cases loaded: {}".format(len(all_cases)))
    all_cases = [case for case in all_cases if type(case) == case_type]
    logger.info("Total {} loaded: {}".format(case_type, len(all_cases)))
    for op in range(n_operators):
        current_partition: List[DomainCase] = []
        used_index: Set[int] = set()
        for cases in range(cases_per_incremental, n_cases, cases_per_incremental):
            for i in range(cases_per_incremental):
                index = randint(0, len(all_cases))
                # TODO: Add randomization options (seed, no-random etc.)
                while index in used_index:
                    index = randint(0, len(all_cases))
                    a_case = all_cases[index]
                    current_partition.append(a_case)
                    used_index.add(index)
            dest_file_path = destination_dir_path + "part" + str(cases) + "cas" + str(op) + "op.dat"
            write_cases(current_partition, dest_file_path)


def create_cases_partitions_continued(n_cases: int, n_operators: int, cases_per_incremental: int,
                                      original_filepath: str, destination_dir_path: str,
                                      case_type: type) -> None:
    """Auxiliary method; Creates the data files with the cases serialized as Python Objects

    Args:
        n_cases (int): Amount of files to be created
        n_operators (int): Amount of operators
        cases_per_incremental (int): Amount of EXTRA cases per partition
        original_filepath (str): Source file with all the cases
        destination_dir_path (str): Directory where the partitions will be stored
        case_type (type): Only the loaded objects of this type will be stored
    """
    all_cases = read_cases_file(original_filepath)
    logger.info("Total cases loaded: {}".format(len(all_cases)))
    all_cases = [case for case in all_cases if type(case) == case_type]
    logger.info("Total {} loaded: {}".format(case_type, len(all_cases)))
    for op in range(n_operators):
        logger.info("Operator {}".format(op))
        current_partition: List[DomainCase] = []
        cases_list: List[int] = []
        for cases in range(0, n_cases, cases_per_incremental):
            cases_in_partition = cases + cases_per_incremental
            logger.info("Partition cases = {} {".format(cases_in_partition))
            for i in range(cases, cases_in_partition):
                # NOTE: Different from the incremental version of the method, here the case selection
                # is not randomized and I don't get the reason
                index = (op * cases_in_partition + i) % len(all_cases)
                cases_list.append(index)
                current_partition.append(all_cases[index])
                logger.info(index)
            logger.info("Current partition size = {}".format(len(current_partition)))
            write_cases(current_partition, destination_dir_path + str(cases_in_partition)
                        + "cas" + str(op) + "op.dat")
        if op == 0:  # NOTE: ???
            for case in current_partition:
                logger.info("tipiNode = {} ; solID = {}".format(case.problem.context.premises[0].content,
                                                                case.solutions[0].conclusion.id))


def create_ordered_case_base() -> List[DomainCase]:
    """???
    TODO
    Returns:
        List[DomainCase]: ???
    """
    # NOTE: I don't know the applications for this method, I just translated it
    cases: List[DomainCase] = read_cases_file("../resources/data/domain_cases/Helpdesk-DomainCases.dat")
    cases_by_category: Dict[int, List[DomainCase]] = {}
    for a_case in cases:
        category_id = int(a_case.problem.context.premises[0].content)
        cases_list = cases_by_category.get(category_id, [])
        cases_list.append(a_case)
        cases_by_category[category_id] = cases_list

    category_quantity: Dict[int, List[int]] = {}
    for c_list in cases_by_category.values():
        categories_list = category_quantity.get(len(c_list), [])
        l_id = int(c_list[0].problem.context.premises[0].content)
        categories_list.append(l_id)
        category_quantity[len(c_list)] = categories_list

    categories_ordered = [category for categories in category_quantity.values() for category in categories]
    categories_ordered.insert(0, 0)

    cases_by_categorical_order = [case for category in categories_ordered for case in cases_by_category.get(category)]
    for a_case in cases_by_categorical_order:
        logger.info(int(a_case.problem.context.premises[0].content))
    return cases_by_categorical_order


def write_cases(cases: List[Union[DomainCase, ArgumentCase]], file_path: str) -> None:
    """Writes the given cases as serialized Python Objevts

    Args:
        cases (List[Union[DomainCase, ArgumentCase]]): List of cases to write
        file_path (str): File path where to write de domain-cases
    """
    try:
        with open(file_path, "wb") as f:
            for case in cases:
                dump(case, f)
    except (IOError, FileNotFoundError) as e:
        logger.exception(e)


def read_cases_file(filename: str) -> List[Union[DomainCase, ArgumentCase]]:
    """Reads the cases serialized Python Objects from a file

    Args:
        filename (str): The file to read

    Returns:
         List[Union[DomainCase, ArgumentCase]]: List containing the loaded cases
    """
    cases: List[DomainCase] = []
    try:
        with open(filename, "rb") as fh:
            case_type = None
            while True:
                aux = load(fh)
                if type(aux) == DomainCase or type(aux) == ArgumentCase:
                    if not case_type or case_type == type(aux):
                        a_case = aux
                        cases.append(a_case)
                        case_type = type(aux)
    except EOFError:
        logger.info("Number of cases: {}".format(len(cases)))
    except (FileNotFoundError, IOError) as e:
        logger.exception(e)
    return cases
