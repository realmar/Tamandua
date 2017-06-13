"""Postprocessor plugin which verifies the field if
the mail-object is tagged as incoming or outgoing."""

from lib.interfaces import IProcessorPlugin
from lib.plugins.plugin_processor import ProcessorData
from lib.plugins.plugin_helpers import get_tag, add_tag


class VerifyIncomingOutgoing(IProcessorPlugin):
    def process(self, obj: ProcessorData) -> None:
        if get_tag(obj.data, 'incoming') is not None:
            pass

        if get_tag(obj.data, 'outgoing') is not None:
            pass
