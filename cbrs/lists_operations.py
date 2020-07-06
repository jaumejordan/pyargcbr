from typing import Sequence, TypeVar, List

T = TypeVar('T')


def merge_lists_using_sets(list1: List[T], list2: Sequence[T]):
    list1 += list(set(list2) - set(list1))


def merge_lists_by_looping(list1: List[T], list2: Sequence[T]):
    for element in list2:
        if element not in list1:
            list1.append(element)
