"""Postprocessor plugin which removed unwanted mail-objects."""

from src.interfaces import IProcessorPlugin
from src.plugins.plugin_processor import ProcessorData, ProcessorAction
from src.plugins.plugin_helpers import check_value


class RemoveUnwanted(IProcessorPlugin):
    __removeRejectReason = [
        'user unknown',
        'account expired'
    ]

    def process(self, obj: ProcessorData) -> None:
        rejectreason = obj.data.get('rejectreason')

        for reason in self.__removeRejectReason:
            if check_value(rejectreason, lambda x: reason in x.lower()):
                obj.action = ProcessorAction.DELETE
                return

        recipient = obj.data.get('recipient')
        if check_value(recipient, lambda x: x.lower() == 'emailtest@phys.ethz.ch'):
            obj.action = ProcessorAction.DELETE
            return

        sender = obj.data.get('sender')
        if check_value(sender, lambda x: x.lower() == 'isg+emailtest@phys.ethz.ch'):
            obj.action = ProcessorAction.DELETE
            return
