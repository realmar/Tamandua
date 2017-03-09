"""Smtpd statistics plugin."""

from lib.plugin_base import PluginBase
import re


class Smtpd(PluginBase):
    """Smtpd statistics plugin."""

    def _define_subscription_regex(self):
        self._subscriptionRegex = re.compile(' postfix\/smtpd')

    def _define_data_regex(self):
        self._dataRegex = re.compile('\/(?P<hostname>[^\s]*) postfix\/smtpd\[[^\]]*\]\: ((?P<servicename_hostname_connect>connect)|(?P<servicename_hostname_disconnect>disconnect)|(?P<queueid>[\w\d]{14}|NOQUEUE))[ :]( (?P<servicename_hostname_action>hold|reject))?(( client=|from |[^m]*m )(?P<client>[^\[]*)\[(?P<ip>[^]]*)\])?(: [^:]*:(?P<reason>[^;]*);)?(.*from=<(?P<servicename_hostname_sender>[^>]*)>)?(.*to=<(?P<servicename_hostname_recipient>[^>]*))?(, [^=]*=[^=]*=(?P<servicename_hostname_bool_saslauth>[^@]*))?')

    def _edit_results(self, results):
        # we remove the stuff we are not interested about
        del results['client']
        del results['ip']
        del results['reason']

        # if results['servicename_hostname_action'] is None:
        #     del results['servicename_hostname_action']

        # then we will concat connect and disconnect
        if results['servicename_hostname_connect'] is not None or results['servicename_hostname_disconnect'] is not None:
            final = results['servicename_hostname_connect']
            if final is None:
                final = results['servicename_hostname_disconnect']

            results['servicename_hostname_communication'] = final
        else:
            results['servicename_hostname_communication'] = None

        del results['servicename_hostname_connect']
        del results['servicename_hostname_disconnect']

        # extract the country from which the email came from.
        # As you can see here doing such things as that is very easy.
        if results['servicename_hostname_sender'] is not None:
            results['servicename_hostname_sender'] = results['servicename_hostname_sender'].split('.')[-1]
        # else:
        #     del results['servicename_hostname_sender']

        if results['servicename_hostname_recipient'] is not None:
            results['servicename_hostname_recipient'] = results['servicename_hostname_recipient'].split('@')[-1]
        # else:
        #     del results['servicename_hostname_recipient']

        if results['servicename_hostname_bool_saslauth'] is None:
            if results['queueid'] is None:
                results['servicename_hostname_saslauth'] = None
                del results['servicename_hostname_bool_saslauth']

        del results['queueid']
