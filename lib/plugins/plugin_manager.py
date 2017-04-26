"""This package contains the PluginManager."""


# used to dynamically import the plugins
import inspect
import os
import sys

# for an explanation please refer to the comments in __loadPlugin
if sys.version_info[1] < 5:
    import importlib.machinery
else:
    import importlib
    import importlib.util

# used for the pre regex
import re

from os.path import join as path_join
from os.path import split as path_split

from ..containers.data_receiver import DataReceiver
from .plugin_base import IPlugin


class PluginManager():
    """Load, instantiate and use all plugins."""

    def __init__(self, absPluginsPath, config):
        """"Constructor of PluginManager."""
        self.__limitHosts = config.get('limit_hosts')
        if self.__limitHosts is None:
            self.__limitHosts = []

        self.dataReceiver = DataReceiver()
        # This regex is used to extract generic information from each
        # log line. Eg. hostname
        self.__preRegex = re.compile(config.get('preregex'))

        self.plugins = None
        self.__load_plugins(absPluginsPath)

    def __load_plugins(self, absPluginsPath):
        """Load all plugins found in the plugins-enabled folder and its subfolders."""
        pluginClasses = []

        modules = []
        # find all files in the plugins-enabled subdir
        for absolute, dirs, files in os.walk(absPluginsPath, followlinks=True):
            for f in files:
                # check if the file is an actual python modul
                if '__init__' not in f and f[-3:] == '.py':
                    # append the absoulte path to it
                    modul = path_join(absolute, f)
                    # Remove the absolute Tamandua path and reformat it.
                    # This will be the namespace in which the module lives
                    #
                    # eg.:
                    #
                    # /some/dir/tamandua/Plugins/test/plugin.py
                    # -->
                    # Plugins.test.plugin
                    modul = modul.replace(
                        absPluginsPath[: absPluginsPath.rfind('/')],
                        '').replace('.py', '')[
                        1:].replace('/', '.')
                    # append a tuple in following form:
                    # ( namespace, absolutepath )
                    pluginGroupName = absolute.replace(absPluginsPath, '')
                    split = path_split(pluginGroupName)
                    #    linux               windows
                    #      v                    v
                    if split[0] == '/' or split[0] == '\\':
                        pluginGroupName = split[1]
                    else:
                        pluginGroupName = split[0]

                    modules.append((modul, path_join(absPluginsPath, absolute, f), pluginGroupName))

        for module in modules:
            if sys.version_info[1] < 5:
                # ref: https://docs.python.org/3/library/importlib.html#importlib.machinery.SourceFileLoader
                # Depricated since 3.6
                imp = importlib.machinery.SourceFileLoader(module[0], module[1]).load_module()
            else:
                # ref: https://docs.python.org/3/library/importlib.html#importlib.util.spec_from_file_location
                # new in python 3.4
                spec = importlib.util.spec_from_file_location(module[0], module[1])
                # ref: https://docs.python.org/3/library/importlib.html#importlib.util.module_from_spec
                # new in python 3.5
                imp = importlib.util.module_from_spec(spec)
                # ref: https://docs.python.org/3/library/importlib.html#importlib.abc.Loader.exec_module
                # new in python 3.4
                spec.loader.exec_module(imp)

            classes = inspect.getmembers(
                imp, lambda cls:
                    isinstance(cls, type) and
                    issubclass(cls, IPlugin))

            pluginClasses.extend(
                [(module[2], cls) for name, cls in classes if name != 'PluginBase' and name != 'SimplePlugin'])

        self.plugins = [(info[0], info[1]()) for info in pluginClasses]

    def process_line(self, line):
        """Extract data from one logline."""
        folderToData = {}

        pre = self.__preRegex.search(line)

        if pre is None:
            # pre = {}
            return
        else:
            pre = pre.groupdict()

        hostname = pre.get('hostname')
        if hostname is not None and hostname not in self.__limitHosts or hostname is None:
            return

        for folderName, plugin in self.plugins:
            if plugin.check_subscription(line):
                if folderToData.get(folderName) is None:
                    folderToData[folderName] = {
                        'pregexdata': pre,
                        'data': [],
                        'raw_logline': line
                    }

                folderToData[folderName]['data'].append(plugin.gather_data(line, pre))

        self.dataReceiver.add_info(folderToData)
