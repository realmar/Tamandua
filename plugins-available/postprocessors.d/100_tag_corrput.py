"""Postprocessor plugin."""

from src.plugins.bases.plugin_processor import ProcessorData
from src.plugins.interfaces import IProcessorPlugin
from src.plugins.plugin_helpers import add_tag


class TagCorrupt(IProcessorPlugin):
    """Postprocessor plugin which tags all object
    which have no tags with the tag 'corrupt'."""

    def process(self, obj: ProcessorData) -> None:
        tags = obj.data.get('tags')
        if tags is None or len(tags) == 0:
            add_tag(obj.data, 'corrupt')