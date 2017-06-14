"""Postprocessor plugin which tags an email for incoming or outgoing."""


from lib.interfaces import IProcessorPlugin
from lib.plugins.plugin_processor import ProcessorData
from lib.plugins.plugin_helpers import add_tag, is_any_dphys_subdomain, check_value


class TagIncomingOutgoing(IProcessorPlugin):
    def process(self, obj: ProcessorData) -> None:
        sender = obj.data.get('sender')
        recipient = obj.data.get('recipient')

        sender_phys = check_value(sender, is_any_dphys_subdomain)
        recipient_phys = check_value(recipient, is_any_dphys_subdomain)

        if sender_phys and recipient_phys:
            add_tag(obj.data, 'intern')
        elif sender_phys and not recipient_phys:
            add_tag(obj.data, 'outgoing')
        elif not sender_phys and recipient_phys:
            add_tag(obj.data, 'incoming')
