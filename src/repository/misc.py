"""Misc classes for the repository."""


import itertools
from enum import Enum
from typing import Iterable, Callable, Generic, TypeVar


class SearchScope(Enum):
    COMPLETE = 1
    INCOMPLETE = 2
    ALL = 3


class StringIsNotAComperator(Exception):
    def __init__(self):
        super().__init__("The given string is not a comparator")


class Comparator():
    greater = '>'
    less = '<'
    greater_or_equal = '>='
    less_or_equal = '<='
    equal = '='
    not_equal = '!='

    def __init__(self, comperator: str):
        for c in (self.equal, self.less, self.greater, self.not_equal, self.greater_or_equal, self.less_or_equal):
            if comperator == c:
                self.comparator = c
                return

        raise StringIsNotAComperator()


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