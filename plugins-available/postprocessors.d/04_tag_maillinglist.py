"""Postprocessor plugin which tags mails from a mailinglist."""

import re

from lib.interfaces import IProcessorPlugin
from lib.plugins.plugin_processor import ProcessorData
from lib.plugins.plugin_helpers import add_tag, is_mailinglist


class TagIncomingOutgoing(IProcessorPlugin):

    def process(self, obj: ProcessorData) -> None:
        sender = obj.data.get('sender')
        recipient = obj.data.get('recipient')

        if is_mailinglist(sender) or is_mailinglist(recipient):
            add_tag(obj.data, 'mailinglist')
