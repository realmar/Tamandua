"""Postprocessor plugin which adds action tags."""

from src.plugins.bases.plugin_processor import ProcessorData
from src.plugins.interfaces import IProcessorPlugin
from src.exceptions import print_warning


class TagAction(IProcessorPlugin):
    """Postprocessing Plugin which sorts the loglines."""

    def process(self, obj: ProcessorData) -> None:
        try:
            obj.data['loglines'].sort()
        except KeyError as e:
            print_warning(str(obj.data) + ' has no loglines.')