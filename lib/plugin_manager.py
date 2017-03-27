"""This package contains the PluginManager."""

from .statistics import Statistics
from .plugin_base import IPlugin

# used to dynamically import the plugins
import importlib
import inspect
import os

# used for the pre regex
import re

from os.path import join as path_join


class PluginManager():
    """Load, instantiate and use all plugins."""

    def __init__(self, absPluginsPath, pattern):
        """"Ctor of PluginManager."""
        self.statistics = Statistics()
        # This regex is used to extract generic information from each
        # log line. Eg. hostname
        self.__pre_regex = re.compile(pattern)

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
                    # remove the absolute Statlyser path and reformat so
                    # that importlib can use it to import it
                    #
                    # eg.:
                    #
                    # /some/dir/statlyser/Plugins/test/plugin.py
                    # -->
                    # Plugins.test.plugin
                    modul = modul.replace(absPluginsPath[:absPluginsPath.rfind('/')], '').replace('.py', '')[1:].replace('/', '.')
                    modules.append(modul)

        for module in modules:
            imp = importlib.import_module(module)

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
            pre = self.__pre_regex.search(line)

            if pre is None:
                pre = {}
            else:
                pre = pre.groupdict()

            extractedData = plugin.gather_data(line, pre)
            if extractedData:
                data.append(extractedData)

        self.statistics.add_info(data)
        self.statistics.increment_line_count()
