"""Postprocessor plugin which tags an email for incoming or outgoing."""

from lib.interfaces import IProcessorPlugin
from lib.plugins.plugin_processor import ProcessorData
from lib.plugins.plugin_helpers import add_tag


class TagIncomingOutgoing(IProcessorPlugin):
    def process(self, obj: ProcessorData) -> None:
        sender = obj.data.get('sender')
        recipient = obj.data.get('recipient')

        if not isinstance(sender, list):
            sender = [sender]

        if not isinstance(recipient, list):
            recipient = [recipient]

        for s in sender:
            if not isinstance(s, str):
                continue

            if 'ethz.ch' in s.lower():
                add_tag(obj.data, 'outgoing')

        for r in recipient:
            if not isinstance(r, str):
                continue

            if 'ethz.ch' in r.lower():
                add_tag(obj.data, 'incoming')
