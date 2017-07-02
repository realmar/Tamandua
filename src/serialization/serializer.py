"""Module which contains the serializer."""

from .interfaces import ISerializable
from .factory import SerializationFactory
from ..config import Config
# used in annotation
from ..containers.data_receiver import DataReceiver


class Serializer():
    """Serializer provides a simple interface to serialize and deserialize data."""

    def __init__(self, config: Config):
        self._serializer = SerializationFactory.get_serializer(config)

    def store(self, dataReceiver: DataReceiver) -> None:
        """Gather data from IDataContainer s and serialize it."""
        serializables = dataReceiver.get_conainers_of_type(ISerializable)
        map = {cls.__class__.__name__: cls.get_serializable_data() for cls in serializables}

        self._serializer.save(map)

    def load(self) -> object:
        """Deserialize data and return it."""
        return self._serializer.load()
