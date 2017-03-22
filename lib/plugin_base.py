"""Here are the base classes of every Plugin."""

from .exceptions import NoSubscriptionRegex, NoDataRegex, RegexGroupsMissing
import abc


class IPlugin(metaclass=abc.ABCMeta):
    """Interface which every plugin has to implement."""

    @abc.abstractmethod
    def _check_subscription(self, line):
        """Return True or False if the subscription regex matched or not."""
        pass

    @abc.abstractmethod
    def _define_subscription_regex(self):
        """Assign the compiled subscription regex to self."""
        pass

    @abc.abstractmethod
    def _define_data_regex(self):
        """Assign the compiled data regex to self."""
        pass

    @abc.abstractmethod
    def gather_data(self, line):
        """Extract the data from a logline and return the results as a dict."""
        pass


class PluginBase(IPlugin):
    """Base class of every plugin, which contains generalized logic."""

    def __init__(self):
        """Ctor of PluginBase."""
        self._subscriptionRegex = None
        self._define_subscription_regex()

        # sanity check of subscription regex
        if self._subscriptionRegex is None:
            raise NoSubscriptionRegex()

        self._dataRegex = None
        self._define_data_regex()

        # sanity check of data regex:
        #
        # it has to be a list at least one item
        if self._dataRegex is None or not isinstance(self._dataRegex, list) or len(self._dataRegex) == 0:
            raise NoDataRegex()

    def __specify_regex_group_name(self, regexMatches, metadata):
        """
        Replace special keywords in the regex match group.

        Those special keywords are:
        hostname    : .group('hostname')
        servicename : __class__.__name__

        Logical keywords:
        bool        : None      --> False
                    : not None  --> True
        """

        newRegexMatches = {}

        for name, value in regexMatches.items():
            newName = name
            hostname = metadata.get('hostname')
            servicename = self.__class__.__name__.lower()

            if name != 'hostname' and hostname is not None:
                newName = newName.replace('hostname', hostname)

            newName = newName.replace('servicename', servicename)

            if 'bool' in name:
                if regexMatches[name] is None:
                    regexMatches[name] = False
                else:
                    regexMatches[name] = True

            newName = newName.replace('_bool', '').replace('_bool', '').replace('_bool_', '')
            newName = newName.replace('hostname_', '').replace('_hostname', '').replace('_hostname_', '')

            if newName != name and name != 'hostname':
                newRegexMatches[newName] = regexMatches[name]

        return newRegexMatches

    def _edit_results(self, results):
        """
        Provide a way for the user to edit the generated result dict.

        This method can be used to add custom stats by interpreting the results,
        eg. add additional reflected information

        Overwrite this method to use it.
        """
        pass

    def _check_subscription(self, line):
        return self._subscriptionRegex.search(line) is not None

    def gather_data(self, line, metadata):
        if not self._check_subscription(line):
            return False

        for regex in self._dataRegex:
            search = regex.search(line)
            isNone = True

            result = search

            # if we did not match or every match is None
            # then we will try the next data regex
            if result is None:
                continue

            result = result.groupdict()

            if not any(result):
                continue

            self._edit_results(result)
            return self.__specify_regex_group_name(result, metadata)

        unknown_data_name = {'servicename_hostname_unknown': None}
        return self.__specify_regex_group_name(unknown_data_name, metadata)
