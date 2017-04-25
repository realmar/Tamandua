from .factory import SerializationFactory
from ..interfaces import ISerializable


class Serializer():
    def __init__(self, config):
        self._serializer = SerializationFactory.get_serializer(config)

    def store(self, dataReceiver):
        serializables = dataReceiver.get_conainers_of_type(ISerializable)
        map = {cls.__class__.__name__: cls.get_serializable_data() for cls in serializables}

        self._serializer.save(map)

    def load(self):
        return self._serializer.load()