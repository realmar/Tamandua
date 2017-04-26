from os.path import join as path_join

from .serialization_methods import JSONSerialization, PickleSerialization
from .exceptions import SerializationMethodNotAvailable


class SerializationFactory():
    @staticmethod
    def get_serializer(config):
        path = path_join(config.get('basepath'), config.get('store_path'))

        if config.get('store_type').lower() == 'json':
            return JSONSerialization(path)
        elif config.get('store_type').lower() == 'pyobj-store':
            return PickleSerialization(path)
        else:
            raise SerializationMethodNotAvailable()