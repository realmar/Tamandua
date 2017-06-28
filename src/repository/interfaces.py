"""This Module contains all interfaces used for the repository."""

from abc import ABCMeta, abstractmethod
from typing import List, Dict
from .misc import SearchScope


class IRepository(metaclass=ABCMeta):
    """"""

    @abstractmethod
    def find(self, query: dict, scope: SearchScope) -> List[Dict]:
        """"""
        pass


    @abstractmethod
    def insert_or_update(self, data: dict, scope: SearchScope) -> None:
        """"""
        pass