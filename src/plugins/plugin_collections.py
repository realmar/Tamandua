"""Module which contains all classes needed for the plugin collection."""


from abc import ABCMeta, abstractmethod
from typing import cast, List

from .interfaces import IDataContainer,     \
                        IPlugin,            \
                        IProcessorPlugin,   \
                        IRequiresPlugins,   \
                        IRequiresRepository,\
                        IAbstractPlugin
from .chain import Chain
from ..repository.factory import RepositoryFactory

try:
    # new in python 3.5.3 #bleedingedge
    # https://docs.python.org/3/library/typing.html#typing.ClassVar
    from typing import ClassVar
except ImportError as e:
    # create a type alias
    from typing import Callable
    ClassVar = Callable


class NoPluginCollectionFound(Exception):
    """Thrown when no plugin collection associated to a given plugin was found."""

    def __init__(self, t: type):
        super().__init__("No associated plugin collection found: plugin type: " + str(t))


class PluginData():
    """Metadata associated with a given plugin."""

    def __init__(self, foldername: str, filename: str, cls: ClassVar):
        self.foldername = foldername
        self.filename = filename
        self.cls = cls


class IPluginCollection(metaclass=ABCMeta):
    """
    Each plugin collection has to implement this interface.

    What is a plugin collection?

    A plugin collection represents, a collection of plugins.
    Each plugin collection stores a given type of plugins. The reason for this is
    that plugins of different types have to be treated differently. (And each
    plugin collection knows how to handle one specific type)
    """

    @abstractmethod
    def add_plugin(self, data: PluginData) -> None:
        """Add a plugin to the plugin collection."""
        pass

    @property
    @abstractmethod
    def plugins(self) -> List[IAbstractPlugin]:
        """Return a list of the stored plugins."""
        pass

    @property
    @abstractmethod
    def subscribed_cls(self) -> type:
        """Return the type of plugins which this collection is responsible."""
        pass


class PluginAssociator():
    """Associate a given plugin with a plugin collection."""

    def __init__(self, pluginManager: 'PluginManager'):
        """Constructor of PluginAssociator."""

        # List[IPluginCollection]
        self._pluginCollections = [
            ContainerPluginCollection(pluginManager),
            DataCollectionPlugins(),
            ProcessorPluginCollection()
        ]

    def add_plugin(self, data: PluginData):
        # cast variable so that it is "typesafe" and a given IDE may do autocompletion
        self.get_collection(data.cls).add_plugin(data)

    def get_collection(self, cls: IAbstractPlugin) -> IPluginCollection:
        for c in self._pluginCollections:
            if issubclass(cls, c.subscribed_cls):
                return c

        raise NoPluginCollectionFound(cast(type, cls))


class BasePluginCollection(IPluginCollection):
    """
    Base class of all plugin collections.
    
    It provides a generic way on how
    to handle a generic type of plugins.
    (Basically just storing them in a list
    and doing nothing more)
    """
    
    def __init__(self):
        self._plugins = []

    def add_plugin(self, data: PluginData) -> None:
        self._plugins.append(data.cls())

    @property
    def plugins(self) -> List[IAbstractPlugin]:
        return self._plugins


class ContainerPluginCollection(BasePluginCollection):
    """
    Plugin collection which stores the plugins of type IDataContainer.
    """

    def __init__(self, pluginManager: 'PluginManager'):
        self.__pluginManager = pluginManager
        super().__init__()

    def add_plugin(self, data: PluginData) -> None:
        inst = data.cls()

        # depending on which additional interfaces this plugin implemented
        # we need to set it up with additional components
        if issubclass(data.cls, IRequiresPlugins):
            inst.set_pluginmanager(self.__pluginManager)

        if issubclass(data.cls, IRequiresRepository):
            inst.set_repository(RepositoryFactory.create_repository())

        self._plugins.append(inst)

    @property
    def subscribed_cls(self) -> type:
        return IDataContainer


class DataCollectionPlugins(BasePluginCollection):
    """
    Plugin collection which store plugins of type IPlugin
    meaning data collection plugins.
    """

    def add_plugin(self, data: PluginData) -> None:
        # additionally to the actual plugin instance
        # we need to store in which folder we found that plugin
        self._plugins.append((data.foldername, data.cls()))

    @property
    def subscribed_cls(self) -> type:
        return IPlugin


class ProcessorPluginCollection(BasePluginCollection):
    """
    Plugin collection which stores plugins of type IProcessor.
    """

    def __init__(self):
        self.__chains = {}
        super().__init__()

    def add_plugin(self, data: PluginData) -> None:
        # processor plugins needs to be chained in a 'Chain'
        # so we construct the 'Chain' add the plugin and store
        # the 'Chain' in the list
        responsibility = data.foldername[:-2]
        handler = (data.filename, data.cls())
        if self.__chains.get(responsibility) is None:
            self.__chains[responsibility] = Chain(responsibility, [handler])
        else:
            self.__chains[responsibility].add_handler(*handler)

    @property
    def plugins(self):
        return self.__chains.values()

    @property
    def subscribed_cls(self) -> type:
        return IProcessorPlugin