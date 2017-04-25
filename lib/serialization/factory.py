from .serialization_methods import JSONSerialization, PickleSerialization
from .exceptions import SerializationMethodNotAvailable


class SerializationFactory():
    @staticmethod
    def get_serializer(config):
        if config.get('store_type').lower() == 'json':
            return JSONSerialization(config.get('store_path'))
        elif config.get('store_type').lower() == 'pyobj-store':
            return PickleSerialization(config.get('store_path'))
        else:
            raise SerializationMethodNotAvailable()