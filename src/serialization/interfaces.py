"""This module contains the interfaces of the serialisation."""


from abc import ABCMeta, abstractmethod


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