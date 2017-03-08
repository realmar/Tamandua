from .exceptions import NoMatch
import abc


class IPlugin(metaclass=abc.ABCMeta):
    @abc.astractmethod
    def _check_subscription(self, line):
        pass

    @abc.abstractmethod
    def _define_subscription_regex(self):
        pass

    @abc.abstractmethod
    def _define_data_regex(self):
        pass

    @abc.abstractmethod
    def gather_data(self, line):
        pass


class PluginBase(IPlugin):
    def __init__(self):
        self._subscriptionRegex = None
        self._define_subscription_regex()

        self._dataRegex = None
        self._define_data_regex()

        self.__regexGroupNames = []
        self.__exract_regex_group_names()

    def __specifize_regex_group_name(self, regexMatches):
        pass

    def __extract_regex_group_names(self):
        pattern = self.__dataRegex.pattern
        lastpos = 0

        while(True):
            pos = pattern.find('?P<', lastpos)
            if pos != -1:
                pos += 3
                closingPos = pattern.find('>', pos)
                self.__regexGroupNames.append(pattern[pos:closingPos])
                lastpos = closingPos
            else:
                break

    def _check_subscription(self, line):
        return self._subscriptionRegex.search(line) is None

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
