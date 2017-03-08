"""This package contains the PluginManager."""

from .statistic import Statistic
from .plugin_base import IPlugin
from .exceptions import NoMatch

# used to dynamically import the plugins
import importlib
import pkgutil
import inspect

from os.path import join as path_join


class PluginManager():
    """Load, instantiate and use all plugins."""

    def __init__(self, absPluginsPath):
        """"Ctor of PluginManager."""
        self.statistic = Statistic()

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
            try:
                data.append(plugin.gather_data(line))
            except NoMatch as e:
                continue

        self.statistic.add_info(data)
