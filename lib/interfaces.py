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
    def process(self, data: dict) -> None:
        pass


class IDataContainer(metaclass=ABCMeta):
    """Public interface of a DataContainer."""

    @property
    @abstractmethod
    def subscribedFolder(self) -> str:
        """Get name of folder which contains relating plugins."""
        pass

    @abstractmethod
    def add_info(self, data: dict) -> None:
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

    @abstractmethod
    def print_integrity_report(self) -> None:
        """
        Prints an integrity report.
        
        Requires build_final() to be run first, in order
        to generate the integrity report.
        """
        pass

class ISerializable(metaclass=ABCMeta):
    """Every class which can be serialized has to implement this interface."""

    @abstractmethod
    def get_serializable_data(self) -> object:
        """Get the data which should be serialized."""
        pass


class ISerializationMethod(metaclass=ABCMeta):
    """Every serialization method has to implement this interface, eg. JSON or PyObjStore."""

    @abstractmethod
    def save(self, data: object) -> None:
        """Serialize data."""
        pass

    @abstractmethod
    def load(self) -> object:
        """Deserialize data and return it."""
        pass