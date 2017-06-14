"""Postprocessor plugin which removed unwanted mail-objects."""

from lib.interfaces import IProcessorPlugin
from lib.plugins.plugin_processor import ProcessorData, ProcessorAction
from lib.plugins.plugin_helpers import check_value


class RemoveUnwanted(IProcessorPlugin):
    def process(self, obj: ProcessorData) -> None:
        recipient = obj.data.get('recipient')
        if check_value(recipient, lambda x: x.lower() == 'emailtest@phys.ethz.ch'):
            obj.action = ProcessorAction.DELETE
            return

        sender = obj.data.get('sender')
        if check_value(sender, lambda x: x.lower() == 'isg+emailtest@phys.ethz.ch'):
            obj.action = ProcessorAction.DELETE
            return

        rejectreason = obj.data.get('rejectreason')
        if check_value(rejectreason, lambda x: 'account expired' in x.lower()):
            obj.action = ProcessorAction.DELETE
            return
