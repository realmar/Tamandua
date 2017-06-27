"""This module contains the Chain class."""


from typing import List, Tuple

from .bases.plugin_processor import ProcessorData, ProcessorAction
from ..interfaces import IProcessorPlugin


class Chain():
    """
    Class which represents a chain of responsibility.

    The precedence of the handlers is given by convention over configuration.
    """

    def __init__(self, responsibility: str, handlers: List[Tuple[str, IProcessorPlugin]] = None):
        """
        Constructor of Chain.

        'handlers' is a list of tuples which contain the filename of the handler
        and an instance of the handler itself (as IProcessorPlugin).
        Data will be given through the handlers in respect of their filenames. If
        a file contains multiple handlers then the order of those handlers may be random.

        'responsibility' defines the type of chain this object represents. This is a string
        which matches to the foldername where the handlers are found.
        Eg.: postprocessors.d --> responsibility = postprocessors

        As you can see, handlers have to be in a folder ending to '.d'
        """
        self.responsibility = responsibility

        if handlers is not None:
            self._handlers = handlers
        else:
            self._handlers = []

        self.__sort_handlers()

    def __sort_handlers(self):
        self._handlers.sort(key=lambda x: x[0])

    def add_handler(self, filename: str, handler: IProcessorPlugin):
        self._handlers.append(
            (filename, handler)
        )
        self.__sort_handlers()

    def process(self, data: ProcessorData) -> None:
        for f, h in self._handlers:
            h.process(data)

            if data.action == ProcessorAction.DELETE:
                return
