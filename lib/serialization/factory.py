"""Module which contains the serialization factory."""

from os.path import join as path_join

from .serialization_methods import JSONSerialization, PickleSerialization, ISerializationMethod
from .exceptions import SerializationMethodNotAvailable

# used in annotation
from ..config import Config


class SerializationFactory():
    """SerializationFactory creates serialization methods."""

    _serializationMethods = {
        'json': JSONSerialization,
        'pyobj-store': PickleSerialization
    }

    @classmethod
    def get_methods(cls) -> list:
        """Return a list of all serialization methods as strings."""
        return list(cls._serializationMethods.keys())

    @classmethod
    def get_serializer(cls, config: Config) -> ISerializationMethod:
        """Return an instance of a serialization method."""
        path = path_join(config.get('basepath'), config.get('store_path'))

        method = cls\
            ._serializationMethods\
            .get(config.get('store_type').lower())

        if not issubclass(method, ISerializationMethod):
            raise SerializationMethodNotAvailable(method.__class__.__name__)
        else:
            return method(path)