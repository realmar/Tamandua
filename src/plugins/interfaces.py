"""This Module contains all interfaces used within Tamandua."""

from abc import ABCMeta, abstractmethod


class IAbstractPlugin():
    """
    Abstract plugin.

    This is a marker interface, which hints a plugin.
    (Used in PluginManager to identify all types of plugins)
    """
    pass


class IPlugin(IAbstractPlugin, metaclass=ABCMeta):
    """Public interface which every plugin has to implement."""

    @abstractmethod
    def check_subscription(self, line: str) -> bool:
        """Return True or False if the subscription regex matched or not."""
        pass

    @abstractmethod
    def gather_data(self, line: str, preRegexMatches: dict) -> dict:
        """Extract the data from a logline and return the results as a dict."""
        pass


class IProcessorPlugin(IAbstractPlugin, metaclass=ABCMeta):
    """
    Interface of a processor plugin.

    A plugin of this type can execute generic
    operations on a given dict.

    Eg.:
    Derivatives of this interface could be used as a postprocessors,
    which modify the mail-objects after their aggregation.
    """

    @abstractmethod
    def process(self, obj: object) -> None:
        """
        Process a given object.

        This method is called by the framework.

        The type of 'obj' is a covariant argument.
        (aka obj may be any derived type of 'object'.
        This is not typesafe but allows for greater
        flexibility.)
        """
        pass


class IRequiresPlugins(metaclass=ABCMeta):
    """
    This class requires plugins and therefore the PluginManager.

    IDataContainer may require plugins to do its work. Therefore
    DataReceiver needs a mean to detect that and assign the
    PluginManager. This interface does exactly that.
    """

    @abstractmethod
    def set_pluginmanager(self, pluginManager: 'PluginManager') -> None:
        """Assign the PluginManager."""
        pass


class IDataContainer(IAbstractPlugin, metaclass=ABCMeta):
    """Public interface of a DataContainer."""

    @property
    @abstractmethod
    def subscribedFolder(self) -> str:
        """Get name of folder which contains relating plugins."""
        pass

    @abstractmethod
    def add_fragment(self, data: dict) -> None:
        """Add data to the container."""
        pass

    @abstractmethod
    def build_final(self) -> None:
        """Aggregate data into final lists and check the data integrity at the same time."""
        pass

    @abstractmethod
    def represent(self) -> None:
        """Print container to STDOUT."""
        pass
