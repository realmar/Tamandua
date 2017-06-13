"""Helper classes of the processor plugins."""

from enum import Enum


class ProcessorAction(Enum):
    KEEP = 1
    DELETE = 2
    NONE = 3


class ProcessorData():
    def __init__(self, data: dict):
        self.__data = data
        self.action = ProcessorAction.KEEP

    @property
    def data(self):
        return self.__data