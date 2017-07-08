"""This Module contains all interfaces used for the repository."""

from abc import ABCMeta, abstractmethod
from typing import List, Dict
from datetime import datetime

from .misc import SearchScope, CountableIterator
from ..expression.builder import Comparator


class IRepository(metaclass=ABCMeta):
    """CRUD"""

    @staticmethod
    @abstractmethod
    def get_config_fields() -> List[str]:
        """"""
        pass

    @abstractmethod
    def find(self, query: dict, scope: SearchScope) -> CountableIterator[Dict]:
        """
        R: Read
        """
        pass

    @abstractmethod
    def count_specific_fields(self, query: dict, field: str, regex=None) -> CountableIterator:
        """"""
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
    def save_size_of_last_logfile(self, pos: int) -> None:
        """"""
        pass

    @abstractmethod
    def get_size_of_last_logfile(self) -> int:
        """"""
        pass

    @abstractmethod
    def make_regexp(self, pattern: str, caseSensitive: True) -> object:
        """"""
        pass

    @abstractmethod
    def make_comparison(self, key: str, value: object, comparator: Comparator) -> object:
        """"""
        pass

    @abstractmethod
    def make_datetime_comparison(self, start: datetime, end: datetime) -> object:
        """"""
        pass

    @abstractmethod
    def get_all_keys(self) -> List[str]:
        """"""
        pass

    @abstractmethod
    def get_all_tags(self) -> List[str]:
        """"""
        pass

    @abstractmethod
    def save_time_of_last_run(self, dt: datetime):
        """"""
        pass