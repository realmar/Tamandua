"""Misc classes for the repository."""


from enum import Enum


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
    equal = '='

    def __init__(self, comperator: str):
        if comperator == '<':
            self.comparator = self.less
        elif comperator == '>':
            self.comparator = self.greater
        elif comperator == '=':
            self.comparator = self.equal
        else:
            raise StringIsNotAComperator()