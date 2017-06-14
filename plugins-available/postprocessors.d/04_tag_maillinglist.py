"""Postprocessor plugin which tags mails from a mailinglist."""

import re

from lib.interfaces import IProcessorPlugin
from lib.plugins.plugin_processor import ProcessorData
from lib.plugins.plugin_helpers import add_tag, check_value


class TagIncomingOutgoing(IProcessorPlugin):
    __maillinglistRegex = re.compile(r'@lists.phys.ethz.ch$', re.IGNORECASE)

    def process(self, obj: ProcessorData) -> None:
        sender = obj.data.get('sender')
        recipient = obj.data.get('recipient')

        predicate = lambda x: self.__maillinglistRegex.search(x) is not None

        sender_list = check_value(sender, predicate)
        recipient_list = check_value(recipient, predicate)

        if sender_list or recipient_list:
            add_tag(obj.data, 'mailinglist')
