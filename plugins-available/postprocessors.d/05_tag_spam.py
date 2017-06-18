"""Postprocessor plugin which adds spam tags."""

from src.interfaces import IProcessorPlugin
from src.plugins.plugin_processor import ProcessorData
from src.plugins.plugin_helpers import add_tag, check_value


class TagSpam(IProcessorPlugin):
    """Postprocessing Plugin which adds spam tags."""

    def process(self, obj: ProcessorData) -> None:
        action = obj.data.get('spamscore')

        if check_value(action, lambda x: x > 5):
            add_tag(obj.data, 'spam')
