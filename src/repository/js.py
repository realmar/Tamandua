"""Module which contains the Loader."""


import os


class Loader():
    """Load external files into tamandua."""

    __basedir = os.path.abspath(os.path.dirname(__file__))

    @classmethod
    def load_js(cls, file: str) -> str:
        """
        Load a js file and return its content.

        path separator is '.' and the '.js' extension is automatically added.
        Eg.: if 'file' is 'mongo_js.mapper' Loader will load
        the 'mongo_js/mapper.js' file.
        """
        path = file.replace('.', os.path.sep) + '.js'
        with open(os.path.join(cls.__basedir, path), 'r') as f:
            content = f.read()

        return content
