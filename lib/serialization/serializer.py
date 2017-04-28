"""Module which contains the serializer."""


from .factory import SerializationFactory
from ..interfaces import ISerializable


class Serializer():
    """Serializer provides a simple interface to serialize and deserialize data."""

    def __init__(self, config):
        self._serializer = SerializationFactory.get_serializer(config)

    def store(self, dataReceiver):
        """Gather data from IDataContainer s and serialize it."""
        serializables = dataReceiver.get_conainers_of_type(ISerializable)
        map = {cls.__class__.__name__: cls.get_serializable_data() for cls in serializables}

        self._serializer.save(map)

    def load(self):
        """Deserialize data and return it."""
        return self._serializer.load()