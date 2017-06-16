"""Postprocessor plugin which adds action tags."""

from src.interfaces import IProcessorPlugin
from src.plugins.plugin_processor import ProcessorData
from src.plugins.plugin_helpers import add_tag, check_value, is_rejected


class TagAction(IProcessorPlugin):
    """Postprocessing Plugin which adds tag depending if the mail was rejected, hold, etc."""

    __rejectReasons = {
        'no_spam_wanted'        : 'no spam wanted',
        'malformed_dns'         : 'malformed dns server reply',
        'domain_not_found'      : 'domain not found',
        'died'                  : 'has passed away',
        'user_unknown'          : 'user unknown',
        'does_not_receive_mail' : 'user does not receive mail on this account anymore',
        'cannot_receive_mail'   : 'account cannot receive e-mail',
        'helo_rejected'         : 'helo command rejected',
        'no_phishing_wanted'    : 'no phishing wanted',
        'malware'               : 'no mail from malware',
        'no_longer_at_dphys'    : 'no longer at eth zurich d-phys',
        'greylisted'            : 'greylisted',
        'relay_denied'          : 'relay access denied',
        'encryption_required'   : 'session encryption is required',
        'client_rejected'       : 'client host rejected'
    }

    def process(self, obj: ProcessorData) -> None:
        action = obj.data.get("action")

        if action == 'hold':
            add_tag(obj.data, 'hold')
        elif is_rejected(obj.data):
            reason = obj.data.get('rejectreason')

            for tag, s in self.__rejectReasons.items():
                if check_value(reason, lambda x: s.lower() in x.lower()):
                    add_tag(obj.data, tag)
                    break