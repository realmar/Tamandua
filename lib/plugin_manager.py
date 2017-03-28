"""This package contains the PluginManager."""

from .statistics import Statistics
from .plugin_base import IPlugin

# used to dynamically import the plugins
import importlib
import importlib.util
import inspect
import os

# used for the pre regex
import re

from os.path import join as path_join


class PluginManager():
    """Load, instantiate and use all plugins."""

    def __init__(self, absPluginsPath, preregexPattern, config):
        """"Ctor of PluginManager."""
        self.__limitHosts = config.get('limit_hosts')
        if self.__limitHosts is None:
            self.__limitHosts = []

        self.statistics = Statistics()
        # This regex is used to extract generic information from each
        # log line. Eg. hostname
        self.__preRegex = re.compile(preregexPattern)

        self.plugins = None
        self.__load_plugins(absPluginsPath)

    def __load_plugins(self, absPluginsPath):
        """Load all plugins found in the Plugins folder and its subfolders."""
        pluginClasses = []

        modules = []
        # find all files in the Plugins subdir
        for absolute, dirs, files in os.walk(absPluginsPath):
            for f in files:
                # check if the file is an actual python modul
                if '__init__' not in f and f[-3:] == '.py':
                    # append the absoulte path to it
                    modul = path_join(absolute, f)
                    # Remove the absolute Statlyser path and reformat it.
                    # This will be the namespace in which the module lives
                    #
                    # eg.:
                    #
                    # /some/dir/statlyser/Plugins/test/plugin.py
                    # -->
                    # Plugins.test.plugin
                    modul = modul.replace(
                        absPluginsPath[: absPluginsPath.rfind('/')],
                        '').replace('.py', '')[
                        1:].replace('/', '.')
                    # append a tulpe in following form:
                    # ( namespace, absolutepath )
                    modules.append((modul, path_join(absPluginsPath, absolute, f)))

        for module in modules:
            # ref: https://docs.python.org/3/library/importlib.html#importlib.util.spec_from_file_location
            spec = importlib.util.spec_from_file_location(module[0], module[1])
            # ref: https://docs.python.org/3/library/importlib.html#importlib.util.module_from_spec
            imp = importlib.util.module_from_spec(spec)
            # ref: https://docs.python.org/3/library/importlib.html#importlib.abc.Loader.exec_module
            spec.loader.exec_module(imp)

            classes = inspect.getmembers(
                imp, lambda cls:
                    isinstance(cls, type) and
                    issubclass(cls, IPlugin))
            # TODO: do not extract potential user defined base classes
            pluginClasses.extend(
                [cls for name, cls in classes if 'PluginBase' not in name])

        self.plugins = [cls() for cls in pluginClasses]

    def process_line(self, line):
        """Extract data from one logline."""
        data = []
        for plugin in self.plugins:
            pre = self.__preRegex.search(line)

            if pre is None:
                pre = {}
            else:
                pre = pre.groupdict()

            hostname = pre.get('hostname')
            if hostname is not None and hostname not in self.__limitHosts:
                break

            extractedData = plugin.gather_data(line, pre)
            if extractedData:
                data.append(extractedData)

        self.statistics.add_info(data)
        self.statistics.increment_line_count()
