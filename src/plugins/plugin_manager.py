"""This module contains the PluginManager."""

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
from typing import cast

from os.path import join as path_join
from os.path import split as path_split
from os.path import sep as path_sep

from ..containers.data_receiver import DataReceiver
from ..interfaces import IAbstractPlugin, IPlugin, IProcessorPlugin
from .plugin_base import PluginBase
from .simple_plugin import SimplePlugin
from .plugin_processor import BaseVerifyProcessor
from .chain import Chain
from ..exceptions import print_exception, print_warning

# used in annotation
from ..config import Config


class PluginManager():
    """Load, instantiate and use all plugins."""

    def __init__(self, absPluginsPath: str, config: Config):
        """"Constructor of PluginManager."""
        self.__limitHosts = config.get('limit_hosts')
        if self.__limitHosts is None:
            self.__limitHosts = []

        self.dataReceiver = DataReceiver(self)
        # This regex is used to extract generic information from each
        # log line. Eg. hostname
        self.__preRegex = re.compile(cast(str, config.get('preregex')))

        self.plugins = []
        self._chains = []
        self.__load_plugins(absPluginsPath)

    def __load_plugins(self, absPluginsPath: str) -> None:
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
                        absPluginsPath[: absPluginsPath.rfind(path_sep)],
                        '').replace('.py', '')[
                        1:].replace(path_sep, '.')
                    # append a tuple in following form:
                    # ( namespace, absolutepath )
                    pluginGroupName = absolute.replace(absPluginsPath, '')
                    split = path_split(pluginGroupName)

                    if split[0] == path_sep:
                        pluginGroupName = split[1]
                    else:
                        pluginGroupName = split[0]

                    modules.append((modul, path_join(absPluginsPath, absolute, f), pluginGroupName, f))

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
                    issubclass(cls, IAbstractPlugin))

            pluginClasses.extend(
                [(module[2], module[3], cls) for name, cls in classes])

        chains = {}
        for info in pluginClasses:
            folderName = info[0]
            fileName = info[1]
            cls = info[2]

            exludePluginTypes = \
                [
                    IAbstractPlugin,
                    IPlugin,
                    IProcessorPlugin,
                    SimplePlugin,
                    PluginBase,
                    BaseVerifyProcessor
                ]

            if cls in exludePluginTypes:
                # if the plugin is any of our base classes we will ignore it.
                continue

            if folderName[-2:] == '.d':
                if not issubclass(cls, IProcessorPlugin):
                    # if the plugin is not a processor then
                    # we will ignore it and warn the user
                    print_warning('Trying to register a processor plugin which is not a processor: ' + folderName + '/'
                                  + fileName + '::' + cls.__name__ + ' - Ignoring plugin.')
                    continue

                rname = folderName[:-2]
                handler = (fileName, cls())
                if chains.get(rname) is None:
                    chains[rname] = [handler]
                else:
                    chains[rname].append(handler)
            else:
                if not issubclass(cls, IPlugin):
                    # if the plugin is not a data collection plugin
                    # we will ignore it and warn the user
                    print_warning('Trying to register a data collection plugin which is not a data collection plugin: '
                                  + folderName + '/' + fileName + '::' + cls.__name__ + ' - Ignoring plugin.')
                    continue

                self.plugins.append((folderName, cls()))

        for responsibility, handlers in chains.items():
            self._chains.append(Chain(responsibility, handlers))

    def get_chain_with_responsibility(self, responsibility: str) -> Chain:
        for c in self._chains:
            if c.responsibility == responsibility:
                return c

    def process_line(self, line: str) -> None:
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

                try:
                    data = plugin.gather_data(line, pre)
                except Exception as e:
                    print_exception(
                        e,
                        "Gathering data from logfile line using plugin: " + plugin.__class__.__name__,
                        "Continue with next plugin",
                        description="You may need to check the mentioned plugin for errors")
                    continue
                else:
                    folderToData[folderName]['data'].append(data)

        self.dataReceiver.add_info(folderToData)
