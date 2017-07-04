"""Plugin which handels forward edge cases."""

import re

from src.plugins.interfaces import IProcessorPlugin
from src.plugins.bases.mail_edge_case_processor import MailEdgeCaseProcessorData
from src import constants


class Pickup(IProcessorPlugin):

    __extract_forwarded_qid_regexp = re.compile(
        'forwarded as (?P<' + constants.PHD_IMAP_QID + r'>[^$]+)')

    def process(self, obj: MailEdgeCaseProcessorData) -> None:
        """
        Merge mails which are locally forwarded on phd-imap.

        This implied that the mail comes from phd-mxin.
        As this is always the case in our setup.
        """

        ns = obj.data

        if ns.origin != constants.PHD_MXIN_QID:
            return

        deliveryrelay = ns.mail.get(constants.DELIVERYRELAY)
        deliverymessage = ns.mail.get(constants.DELIVERYMESSAGE)

        if deliveryrelay is None or deliverymessage is None:
            return

        if deliveryrelay != 'local':
            return

        forwardedqid_q = self.__extract_forwarded_qid_regexp.search(deliverymessage)

        if forwardedqid_q is None:
            return

        forwardedqid = forwardedqid_q.groupdict().get(constants.PHD_IMAP_QID)

        if forwardedqid is None:
            return

        imapmail = ns.map_qid_imap.get(forwardedqid)

        if imapmail is None:
            return

        ns.merge_data(ns.mail, imapmail)

        msgid = ns.mail.get(constants.MESSAGEID)

        def msgid_agg_wrapp(msgid):
            msgidmail = ns.map_msgid.get(msgid)

            if msgidmail is not None:
                if isinstance(msgidmail, list):
                    for m in msgidmail:
                        ns.merge_data(ns.mail, m)
                else:
                    ns.merge_data(ns.mail, msgidmail)

                del ns.map_msgid[msgid]

        if isinstance(msgid, list):
            for m in msgid:
                msgid_agg_wrapp(m)
        else:
            msgid_agg_wrapp(msgid)

        del ns.map_qid_imap[forwardedqid]

