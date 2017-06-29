"""This Module contains all interfaces used for the repository."""

from abc import ABCMeta, abstractmethod
from typing import List, Dict

from .misc import SearchScope


class IRepository(metaclass=ABCMeta):
    """CRUD"""

    @abstractmethod
    def find(self, query: dict, scope: SearchScope) -> List[Dict]:
        """
        R: Read
        """
        pass

    @abstractmethod
    def insert_or_update(self, data: dict, scope: SearchScope) -> None:
        """
        C: Create
        or
        U: Update
        """
        pass

    @abstractmethod
    def delete(self, query: dict, scope: SearchScope) -> None:
        """
        D: Delete
        """
        pass

    @abstractmethod
    def remove_metadata(self, data: dict) -> None:
        """"""
        pass