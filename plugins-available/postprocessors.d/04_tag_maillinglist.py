"""Postprocessor plugin which tags mails from a mailinglist."""

from src.plugins.bases.plugin_processor import ProcessorData
from src.plugins.interfaces import IProcessorPlugin
from src.plugins.plugin_helpers import add_tag, is_mailinglist


class TagMailinglist(IProcessorPlugin):
    """Tag mail from mailinglists."""

    def process(self, obj: ProcessorData) -> None:
        sender = obj.data.get('sender')
        recipient = obj.data.get('recipient')

        if is_mailinglist(sender) or is_mailinglist(recipient):
            add_tag(obj.data, 'mailinglist')
