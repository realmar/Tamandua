"""Preprocessor plugin which removes all tags."""

from src.plugins.bases.plugin_processor import ProcessorData
from src.plugins.interfaces import IProcessorPlugin


class RemoveUnwanted(IProcessorPlugin):
    def process(self, obj: ProcessorData) -> None:
        try:
            del obj.data['tags']
        except KeyError as e:
            # this obj has no tags
            pass

