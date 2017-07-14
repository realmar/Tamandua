"""Misc classes for the repository."""


from enum import Enum
from typing import Iterable, Callable, Generic, TypeVar


class SearchScope(Enum):
    """
    SearchScope defines in which scope a given action
    should be executed in the storage backend.

    Note that ALL is not applicable to all methods in
    IRepository. For example you cannot insert_or_update
    in ALL scopes.
    """

    COMPLETE = 1
    INCOMPLETE = 2
    ALL = 3


T = TypeVar('T')


class CountableIterator(Generic[T]):
    """
    Custom iterator which supports counting its elements.

    Although in order for this to work, you need supply a function
    which defines how to count a given iterator.
    """

    def __init__(self, data: Iterable[T], len_counter: Callable[[Iterable[T]], int]):
        """Constructor of CountableIterator."""
        self.__data = data
        self.__len_counter = len_counter

    def __iter__(self) -> Iterable:
        """Get iterator."""
        return self

    def __next__(self):
        """Return the next item in the iterator."""
        return next(self.__data)

    def __len__(self):
        """Count iterator using the given count function."""
        return self.__len_counter(self.__data)
