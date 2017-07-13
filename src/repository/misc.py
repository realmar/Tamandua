"""Misc classes for the repository."""


from enum import Enum
from typing import Iterable, Callable, Generic, TypeVar


class SearchScope(Enum):
    COMPLETE = 1
    INCOMPLETE = 2
    ALL = 3


T = TypeVar('T')


class CountableIterator(Generic[T]):
    """Custom iterator which supports counting its elements."""

    def __init__(self, data: Iterable[T], len_counter: Callable[[Iterable[T]], int]):
        self.__data = data
        self.__len_counter = len_counter

    def __iter__(self) -> Iterable:
        return self

    def __next__(self):
        return next(self.__data)

    def __len__(self):
        return self.__len_counter(self.__data)
