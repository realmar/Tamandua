""""""


from abc import ABCMeta, abstractmethod
from typing import cast, List

from .interfaces import IDataContainer, IPlugin, IProcessorPlugin, IRequiresPlugins, IAbstractPlugin
from .chain import Chain

try:
    # new in python 3.5.3 #bleedingedge
    # https://docs.python.org/3/library/typing.html#typing.ClassVar
    from typing import ClassVar
except ImportError as e:
    # create a type alias
    from typing import Callable
    ClassVar = Callable


class NoPluginCollectionFound(Exception):
    def __init__(self, t: type):
        super().__init__("No associated plugin collection found: plugin type: " + str(t))


class PluginData():
    def __init__(self, foldername: str, filename: str, cls: ClassVar):
        self.foldername = foldername
        self.filename = filename
        self.cls = cls


class IPluginCollection(metaclass=ABCMeta):
    @abstractmethod
    def add_plugin(self, data: PluginData) -> None:
        pass

    @property
    @abstractmethod
    def plugins(self) -> List[IAbstractPlugin]:
        pass

    @property
    @abstractmethod
    def subscribed_cls(self) -> type:
        pass


class PluginAssociator():
    def __init__(self, pluginManager: 'PluginManager'):
        # List[IPluginCollection]
        self._pluginCollections = [
            ContainerPluginCollection(pluginManager),
            DataCollectionPlugins(),
            ProcessorPluginCollection()
        ]

        """
        # optimize collection getter for cpu
        # NOTE: this will NOT work
        self.__collection_map = {}
        for c in self._pluginCollections:
            self.__collection_map[c.subscribed_cls] = c
        """


    def add_plugin(self, data: PluginData):
        # cast variable so that it is "typesafe" and a given IDE may do autocompletion
        self.get_collection(data.cls).add_plugin(data)

    def get_collection(self, cls: IAbstractPlugin) -> IPluginCollection:
        # TODO: REFACTOR: Optimize!! This is very expensive.

        for c in self._pluginCollections:
            if issubclass(cls, c.subscribed_cls):
                return c

        raise NoPluginCollectionFound(cast(type, cls))

        """
        try:
            return self.__collection_map[cls]
        except Exception as e:
            raise NoPluginCollectionFound(cast(type, cls))
        """


class BasePluginCollection(IPluginCollection):
    def __init__(self):
        self._plugins = []

    def add_plugin(self, data: PluginData) -> None:
        self._plugins.append(data.cls())

    @property
    def plugins(self) -> List[IAbstractPlugin]:
        return self._plugins


class ContainerPluginCollection(BasePluginCollection):
    def __init__(self, pluginManager: 'PluginManager'):
        self.__pluginManager = pluginManager
        super().__init__()

    def add_plugin(self, data: PluginData) -> None:
        inst = data.cls()

        if issubclass(data.cls, IRequiresPlugins):
            inst.set_pluginmanager(self.__pluginManager)

        self._plugins.append(inst)

    @property
    def subscribed_cls(self) -> type:
        return IDataContainer


class DataCollectionPlugins(BasePluginCollection):
    def add_plugin(self, data: PluginData) -> None:
        self._plugins.append((data.foldername, data.cls()))

    @property
    def subscribed_cls(self) -> type:
        return IPlugin


class ProcessorPluginCollection(BasePluginCollection):
    def __init__(self):
        self.__chains = {}
        super().__init__()

    def add_plugin(self, data: PluginData) -> None:
        responsibility = data.foldername[:-2]
        handler = (data.filename, data.cls())
        if self.__chains.get(responsibility) is None:
            self.__chains[responsibility] = Chain(responsibility, [handler])
        else:
            self.__chains[responsibility].add_handler(data.filename, handler)

    @property
    def subscribed_cls(self) -> type:
        return IProcessorPlugin