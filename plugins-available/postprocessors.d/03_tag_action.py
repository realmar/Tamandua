"""Postprocessor plugin which adds action tags."""

from src.interfaces import IProcessorPlugin
from src.plugins.plugin_processor import ProcessorData
from src.plugins.plugin_helpers import add_tag, check_value, is_rejected


class TagAction(IProcessorPlugin):
    """Postprocessing Plugin which adds tag depending if the mail was rejected, hold, etc."""

    __rejectReasons = [
        'no spam wanted',
        'malformed dns server reply',
        'domain not found',
        'has passed away',
        'user unknown',
        'user does not receive mail on this account anymore',
        'account cannot receive e-mail',
        'helo command rejected',
        'no phishing wanted',
        'no mail from malware',
        'no longer at eth zurich d-phys',
        'greylisted',
        'relay access denied',
        'session encryption is required',
        'client host rejected'
    ]

    def process(self, obj: ProcessorData) -> None:
        action = obj.data.get("action")

        if action == 'hold':
            add_tag(obj.data, 'hold')
        elif is_rejected(obj.data):
            reason = obj.data.get('rejectreason')

            for r in self.__rejectReasons:
                if check_value(reason, lambda x: r.lower() in x.lower()):
                    add_tag(obj.data, 'reject')
                    break