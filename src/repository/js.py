""""""


import os


class Loader():
    """"""

    __basedir = os.path.abspath(os.path.dirname(__file__))

    @classmethod
    def load_js(cls, file: str) -> str:
        path = file.replace('.', os.path.sep) + '.js'
        with open(os.path.join(cls.__basedir, path), 'r') as f:
            content = f.read()

        return content
