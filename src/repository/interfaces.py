"""This Module contains all interfaces used for the repository."""

from abc import ABCMeta, abstractmethod
from typing import List, Dict

from .misc import SearchScope


class IRepository(metaclass=ABCMeta):
    """CRUD"""

    @staticmethod
    @abstractmethod
    def get_config_fields() -> List[str]:
        """"""
        pass

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

    @abstractmethod
    def save_position_of_last_read_byte(self, pos: int) -> None:
        """"""
        pass

    @abstractmethod
    def get_position_of_last_read_byte(self) -> int:
        """"""
        pass

    @abstractmethod
    def make_regexp(self, pattern: str) -> object:
        """"""
        pass

    @abstractmethod
    def get_all_keys(self) -> List[str]:
        """"""
        pass