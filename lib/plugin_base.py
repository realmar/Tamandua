"""Here are the base classes of every Plugin."""

from .exceptions import NoMatch
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

        self._dataRegex = None
        self._define_data_regex()

        self.__regexGroupNames = []
        self.__extract_regex_group_names()

    def __specifize_regex_group_name(self, regexMatches):
        """
        Replace special keywords in the regex match group.

        Those special keywords are:
        hostname    : .group('hostname')
        servicename : __class__.__name__
        """

        for name, value in regexMatches.items():
            newName = None
            separateNames = name.split('_')
            hostname = regexMatches.get('hostname')
            servicename = self.__class__.__name__.lower()

            if hostname is not None:
                if name != 'hostname':
                    newName = name.replace('hostname', hostname)

            if 'servicename' in separateNames:
                if newName is None:
                    newName = name

                newName = newName.replace('servicename', servicename)

            if newName is not None:
                # if we still have an empty hostname in the key we will remove it
                newName = newName.replace('hostname_', '').replace('_hostname', '')

                regexMatches[newName] = regexMatches.pop(name)

        try:
            del regexMatches['hostname']
        except Exception as e:
            # if we catch an exception this means that the given
            # dict key does not exists
            pass

    def __extract_regex_group_names(self):
        """Extract the group names of a regex."""
        pattern = self._dataRegex.pattern
        lastpos = 0

        while(True):
            startPos = pattern.find('?P<', lastpos)
            if startPos != -1:
                startPos += 3
                endPos = pattern.find('>', startPos)
                self.__regexGroupNames.append(pattern[startPos:endPos])
                lastpos = endPos
            else:
                break

    def _check_subscription(self, line):
        return self._subscriptionRegex.search(line) is not None

    def gather_data(self, line):
        if not self._check_subscription(line):
            raise NoMatch()

        search = self._dataRegex.search(line)
        result = {}

        for group in self.__regexGroupNames:
            try:
                result[group] = search.group(group)
            except Exception as e:
                # This means that the regex didnt match
                # to the named group
                result[group] = None

        self.__specifize_regex_group_name(result)
        return result
