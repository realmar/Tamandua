"""Config model."""

import json
from .exceptions import MissingConfigField, InvalidConfigField
from .serialization.factory import SerializationFactory


class Config():
    """Store and validate the tamandua config."""

    def __init__(self, configpath: str, basepath: str, overwrite: dict = None):
        """Load config as YAML into memory."""
        with open(configpath, 'r') as f:
            self.__config = json.load(f)

        if isinstance(overwrite, dict):
            for k, v in overwrite.items():
                if v is not None:
                    self.__config[k] = v

        self.__validate()
        self.__config['basepath'] = basepath

    def __validate(self) -> None:
        """Validate the config and raise exceptions."""
        for name in ('preregex', 'store_type', 'store_path'):
            if self.__config.get(name) is None:
                raise MissingConfigField(name)

        if self.__config.get('store_type') not in SerializationFactory.get_methods():
            raise InvalidConfigField('store_type', SerializationFactory.get_methods())

    def get(self, key: str) -> object:
        """Get a config attribute."""
        return self.__config.get(key)