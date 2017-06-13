"""Postprocessor plugin which removed unwanted mail-objects."""

from lib.interfaces import IProcessorPlugin
from lib.plugins.plugin_processor import ProcessorData, ProcessorAction


class RemoveUnwanted(IProcessorPlugin):
    def process(self, obj: ProcessorData) -> None:
        recipient = obj.data.get('recipient')
        if not isinstance(recipient, list):
            recipient = [recipient]

        for r in recipient:
            if not isinstance(r, str):
                continue

            if r.lower() == 'emailtest@phys.ethz.ch':
                    obj.action = ProcessorAction.DELETE
