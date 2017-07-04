"""Plugin which handels pickup edge cases."""

from src import constants
from src.plugins.interfaces import IProcessorPlugin
from src.plugins.bases.mail_edge_case_processor import MailEdgeCaseProcessorData


class Pickup(IProcessorPlugin):
    def process(self, obj: MailEdgeCaseProcessorData) -> None:
        ns = obj.data
        msgid = ns.mail.get(constants.MESSAGEID)

        if msgid is None:
            return

        for qid, m in ns.map_pickup.items():
            for k, v in m.items():
                if k == constants.MESSAGEID and msgid == v:
                    ns.merge_data(ns.mail, m)
                    del ns.map_pickup[qid]
                    return
