"""Postprocessor plugin which adds action tags."""

from lib.interfaces import IProcessorPlugin
from lib.plugins.plugin_processor import ProcessorData
from lib.plugins.plugin_helpers import add_tag, check_value


class TagAction(IProcessorPlugin):
    """Postprocessing Plugin which adds tag depending if the mail was rejected, hold, etc."""

    def process(self, obj: ProcessorData) -> None:
        action = obj.data.get("action")

        if action == 'hold':
            add_tag(obj.data, 'hold')
        elif action == 'reject':
            reason = obj.data.get('rejectreason')
            if check_value(reason, lambda x: 'greylisted' in x.lower()):
                add_tag(obj.data, 'greylisted')
            elif check_value(reason, lambda x: 'account expired' in x.lower()):
                add_tag(obj.data, 'account_expired')