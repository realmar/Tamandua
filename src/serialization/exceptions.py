"""Custom Exceptions used by the serialization."""


class SerializationMethodNotAvailable(Exception):
    def __init__(self, name):
        super().__init__("The given serialization method is not available: " + name)