"""Config model."""

import yaml


class Config():
    """Store and validate the statlyser config."""

    def __init__(self, configpath):
        """Load config as YAML into memory."""
        with open(configpath, 'r') as f:
            self.__config = yaml.load(f)

    def __validate(self):
        """Validate the config, currently not needed."""
        pass

    def get(self, key):
        """Get a config attribute."""
        return self.__config.get(key)
