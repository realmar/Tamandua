"""Custom Exceptions used by the Application."""

import colorama
import inspect
import sys
import os

from . import constants


class NoSubscriptionRegex(Exception):
    def __init__(self, clsname):
        super().__init__("No subscription regex defined in: " + clsname)


class NoDataRegex(Exception):
    def __init__(self, clsname):
        super().__init__("No data regex defined in: " + clsname)


class RegexGroupsMissing(Exception):
    def __init__(self, clsname, pattern):
        super().__init__("No named regex groups defined in: " + clsname + " pattern: " + pattern)


class MissingConfigField(Exception):
    def __init__(self, field):
        super().__init__("The following field is missing from the config: " + field)


class InvalidConfigField(Exception):
    def __init__(self, field, allowedValues):
        super().__init__("The following field in the config is wrong: " + field + " allowed values are following: " + str(allowedValues))


class MultipleDataSetsUnknown(Exception):
    def __init__(self, clsname):
        super().__init__(clsname + """ has received multiple datasets for
        unknown data. This is either a bug, or you have a custom PluginBase
        class which does something wrong in gather_data. """)


class InvalidRegexFlag(Exception):
    def __init__(self, clsname, pattern):
        super().__init__("Invalid regex-flag in: " + clsname + " pattern: " + pattern)


def print_exception(e: Exception, cause: str, measure: str, fatal: bool=False, description: str="Not available") -> None:
    """Prints an exception and additional information."""

    preStr = ''
    if fatal:
        preStr = 'Fatal '

    print(colorama.Fore.RED + preStr + 'Exception happened:')
    print(colorama.Style.BRIGHT + 'Cause: ' + colorama.Style.NORMAL + cause)
    print(colorama.Style.BRIGHT + 'Message: ' + colorama.Style.NORMAL + str(e))
    print(colorama.Style.BRIGHT + 'Description: ' + colorama.Style.NORMAL + description)
    print(colorama.Style.BRIGHT + 'Measure: ' + colorama.Style.NORMAL + measure)

    try:
        if sys.version_info[1] >= 5:
            # if the python version is greater than 3.5
            # we can provide the user with more precise
            # information where the exception took place
            #
            # Why >= 3.5?
            # Because in

            trace = inspect.trace()[0]

            print(colorama.Style.BRIGHT + 'File: ' + colorama.Style.NORMAL + str(trace[1]))
            print(colorama.Style.BRIGHT + 'Line: ' + colorama.Style.NORMAL + str(trace[2]))
            print(colorama.Style.BRIGHT + 'Function: ' + colorama.Style.NORMAL + str(trace[3]))
    except Exception as e:
        pass

    # if we are in a development env we will reraise the exception
    env = os.environ.get(constants.TAMANDUAENV)
    if env == constants.DEVENV:
        raise e


def print_warning(msg):
    """Prints a warning."""

    print(
        colorama.Style.BRIGHT + colorama.Fore.YELLOW +
        'Warning: ' +
        colorama.Fore.RESET + colorama.Style.RESET_ALL + msg)