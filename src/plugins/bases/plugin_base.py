"""Here are the base classes of every Plugin."""

import abc
from enum import Enum
from ast import literal_eval

from ...exceptions import NoSubscriptionRegex, NoDataRegex, RegexGroupsMissing, InvalidRegexFlag
from ...interfaces import IPlugin


class RegexFlags(Enum):
    STORETIME = 1,
    PICKUP = 2


class PluginBase(IPlugin, metaclass=abc.ABCMeta):
    """Base class of every plugin, which contains generalized logic."""

    def __init__(self):
        """Constructor of PluginBase."""
        self._subscriptionRegex = None
        self._define_subscription_regex()

        # sanity check of subscription regex
        if self._subscriptionRegex is None:
            raise NoSubscriptionRegex(self.__class__.__name__)

        self._dataRegex = None
        self._define_data_regex()

        # sanity check of data regex:
        #
        # it has to be a list at least one item
        if self._dataRegex is None or not isinstance(self._dataRegex, list) or len(self._dataRegex) == 0:
            raise NoDataRegex(self.__class__.__name__)

        # check content of this list
        newDataRegex = []
        for dataRegex in self._dataRegex:
            if not isinstance(dataRegex, tuple):
                newDataRegex.append((dataRegex, ()))
                continue
            else:
                if len(dataRegex) != 2:
                    # testing interface of regex
                    try:
                        m = dataRegex[0].search
                    except Exception as e:
                        raise NoDataRegex(self.__class__.__name__)

                    newDataRegex.append((dataRegex[0], ()))
                    continue

                for flag in dataRegex[1]:
                    if not isinstance(flag, RegexFlags):
                        raise InvalidRegexFlag(self.__class__.__name__, dataRegex[0].pattern)

            newDataRegex.append(dataRegex)
        self._dataRegex = newDataRegex

        r, info = self.__check_data_regex_group_names()
        if r:
            raise RegexGroupsMissing(self.__class__.__name__, info)

    @abc.abstractmethod
    def _define_subscription_regex(self) -> None:
        """Assign the compiled subscription regex to self."""
        pass

    @abc.abstractmethod
    def _define_data_regex(self) -> None:
        """Assign the compiled data regex to self."""
        pass

    def check_subscription(self, line: str) -> bool:
        return self._subscriptionRegex.search(line) is not None

    def __check_data_regex_group_names(self) -> tuple:
        """
        Check if the user has any named groups defined in the regex.

        return:
        False when there are groups
        True when there are no groups
        """
        for regex, flags in self._dataRegex:
            if '?P<' not in regex.pattern:
                return True, regex.pattern

        return False, None

    def _specify_regex_group_name(self, dataRegexMatches: dict, preRegexMatches: dict) -> dict:
        """
        Replace special keywords in the regex match group.

        Those special keywords are:
        hostname    : .group('hostname')
        servicename : __class__.__name__

        Logical keywords:
        BOOL        : None      --> False
                    : not None  --> True

        Example:

        hostname_servicename_saslauth_BOOL
        └────────┬─────────┘         └─┬─┘
            replacement              flags
            keywords
        """

        newDataRegexMatches = {}

        for key, value in dataRegexMatches.items():
            newName = key
            hostname = preRegexMatches.get('hostname')
            servicename = self.__class__.__name__.lower()

            if key != 'hostname' and hostname is not None:
                newName = newName.replace('hostname', hostname)

            newName = newName.replace('servicename', servicename)

            if 'BOOL' in key:
                if dataRegexMatches[key] is None:
                    dataRegexMatches[key] = False
                else:
                    dataRegexMatches[key] = True

            keySplit = newName.split('_')
            for toBeRemoved in ('hostname', 'BOOL'):
                try:
                    keySplit.remove(toBeRemoved)
                except ValueError as e:
                    pass
            newName = '_'.join(keySplit)

            newDataRegexMatches[newName] = dataRegexMatches[key]

        return newDataRegexMatches

    def _edit_results(self, results: dict) -> None:
        """
        Provide a way for the user to edit the generated result dict.

        This method can be used to add custom stats by interpreting the results,
        eg. add additional reflected information

        Overwrite this method to use it.
        """
        pass

    def gather_data(self, line: str, preRegexMatches: dict) -> tuple:
        for regex, flags in self._dataRegex:
            search = regex.search(line)

            # if we did not match or every match is None
            # then we will try the next data regex
            if search is None:
                continue

            # remove leading and trailing whitspaces from values
            def strip(v: str) -> str:
                if isinstance(v, str):
                    return v.strip()
                else:
                    return v

            def le(input: str) -> object:
                try:
                    # try interpreting the string as a type
                    return literal_eval(input)
                except Exception as e:
                    # if we fail, then we will simply return the original input
                    return input

            result = {key: le(strip(value)) for key, value in search.groupdict().items()}

            if not any(v is not None for v in result.values()):
                continue

            self._edit_results(result)
            return True, flags, self._specify_regex_group_name(result, preRegexMatches)

        unknown_data_name = {'servicename_hostname': 'unknown'}
        return False, (), self._specify_regex_group_name(unknown_data_name, preRegexMatches)
