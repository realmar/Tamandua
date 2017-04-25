"""This Module contains all interfaces used within Tamandua."""


from abc import ABCMeta, abstractmethod


class IPlugin(metaclass=ABCMeta):
    """Public interface which every plugin has to implement."""

    @abstractmethod
    def check_subscription(self, line: str) -> bool:
        """Return True or False if the subscription regex matched or not."""
        pass

    @abstractmethod
    def gather_data(self, line: str, preRegexMatches: dict) -> dict:
        """Extract the data from a logline and return the results as a dict."""
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
    def represent(self) -> None:
        """Print container to STDOUT."""
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