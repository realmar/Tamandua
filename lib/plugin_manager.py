"""This package contains the PluginManager."""

from .statistics import Statistics
from .plugin_base import IPlugin

# used to dynamically import the plugins
import importlib
import pkgutil
import inspect

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

        modules = pkgutil.walk_packages(path_join(absPluginsPath, '.'))
        for module in modules:
            # TODO: do not hardcode the name of main (statlyser)
            if not module[2] and module[1].lower() != 'statlyser':
                imp = importlib.import_module(module[1])

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
