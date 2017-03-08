"""This package contains the PluginManager."""

from .statistic import Statistic
from .plugin_base import IPlugin
from .exceptions import NoMatch

# used to dynamically import the plugins
import importlib
import pkgutil


class PluginManager():
    """Load, instantiate and use all plugins."""

    def __init__(self, absPluginsPath):
        """"Ctor of PluginManager."""
        self.statistic = Statistic()
        self.plugins = self.__load_plugins(absPluginsPath)

    def __load_plugins(self, absPluginsPath):
        """Load all plugins found in the Plugins folder and its subfolders."""
        pluginClasses = []

        modules = pkgutil.walk_packages(absPluginsPath)
        for module in modules:
            # TODO: do not hardcode the name of main (statlyser)
            if not module[2] and module[1] != 'statlyser':
                imp = importlib.import_module(module[1])
                classes = [cls for name, cls in imp.__dict__.items() if isinstance(cls, type) and issubclass(cls, IPlugin)]
                pluginClasses.extend(classes)

        return [cls() for cls in pluginClasses]

    def process_line(self, line):
        """Extract data from one logline."""
        for plugin in self.plugins:
            try:
                self.statistic.add_info(plugin.gather_data(line))
            except NoMatch as e:
                continue
