"""Postprocessor plugin."""

import re

from lib.plugins.plugin_processor import BaseVerifyProcessor, ProcessorData
from lib.plugins.plugin_helpers import has_tag, is_rejected, get_max, is_mailinglist, check_value
import lib.constants as constants


class VerifyDelivery(BaseVerifyProcessor):
    """Verify delivery."""

    # regex which matches loglines on phd-imap which show localhost as connecting client
    # those loglines hit a mail from a mailinglist directly from imap
    __imapLocalhostClientRegex = re.compile(r'phd-imap\spostfix\/smtpd\[[^\]]+?\]:\s[^\:]+?\:\sclient=localhost\[[^\]]+?\]')

    def _setup(self) -> None:
        self._matchingTags = ['incoming', 'outgoing', 'internal', 'relay']
        self._requiredFields = [
            constants.MESSAGEID,
            'size',
            'sender',
            'recipient'
        ]

    def _custom_match(self, obj: ProcessorData) -> bool:
        if is_rejected(obj.data):
            return False
        else:
            raise NotImplementedError()

    def _get_additional_fields(self, obj: ProcessorData) -> list:
        fields = []

        messageid = obj.data.get(constants.MESSAGEID)

        if not (is_mailinglist(obj.data.get('sender')) and
                check_value(
                    obj.data.get('loglines'),
                    lambda x: self.__imapLocalhostClientRegex.search(x) is not None
                )):
            fields.extend([
                constants.PHD_MXIN_QID,
                constants.PHD_MXIN_TIME
            ])

            if messageid != '':
                fields.extend([
                    'virusresult',
                    'virusaction'
                ])

        virusresult = obj.data.get('virusresult')
        if messageid != '' and virusresult is not None and 'Blocked INFECTED' not in virusresult:
            fields.extend([
                constants.PHD_IMAP_QID,
                constants.PHD_IMAP_TIME,
            ])

        size = get_max(obj.data.get('size'))

        if size is not None and messageid != '':
            if size < 1024 and not has_tag(obj.data, 'outgoing'):
                fields.extend([
                    'spamdesc',
                    'spamrequiredscore',
                    'spamscantime',
                    'spamscore',
                    constants.UID,
                    constants.USERNAME
                ])

        return fields