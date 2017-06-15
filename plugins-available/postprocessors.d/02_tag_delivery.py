"""Postprocessor plugin."""


from lib.interfaces import IProcessorPlugin
from lib.plugins.plugin_processor import ProcessorData
from lib.plugins.plugin_helpers import \
                                        add_tag, \
                                        is_dphys_subdomain, \
                                        check_value, \
                                        is_rejected


class TagDelivery(IProcessorPlugin):
    """Tag mails depending on their mail addresses."""

    def process(self, obj: ProcessorData) -> None:
        if is_rejected(obj.data):
            return

        sender = obj.data.get('sender')
        recipient = obj.data.get('recipient')

        if sender is None or recipient is None:
            return

        sender_phys = check_value(sender, is_dphys_subdomain)
        recipient_phys = check_value(recipient, is_dphys_subdomain)

        if sender_phys and recipient_phys:
            add_tag(obj.data, 'intern')
        elif sender_phys and not recipient_phys:
            add_tag(obj.data, 'outgoing')
        elif not sender_phys and recipient_phys:
            add_tag(obj.data, 'incoming')
        elif not sender_phys and not recipient_phys:
            add_tag(obj.data, 'relaying')
