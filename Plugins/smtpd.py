"""Smtpd statistics plugin."""

from lib.plugin_base import PluginBase
import re


class Smtpd(PluginBase):
    """Smtpd statistics plugin."""

    def _define_subscription_regex(self):
        self._subscriptionRegex = re.compile(' postfix\/smtpd')

    def _define_data_regex(self):
        self._dataRegex = re.compile('\/(?P<hostname>[^\s]*) postfix\/smtpd\[[^\]]*\]\: ((?P<servicename_connect>connect)|(?P<servicename_disconnect>disconnect)|(?P<queueid>[\w\d]{14}|NOQUEUE))[ :]( (?P<servicename_action>hold|reject))?(( client=|from |[^m]*m )(?P<client>[^\[]*)\[(?P<ip>[^]]*)\])?(: [^:]*:(?P<reason>[^;]*);)?(.*from=<(?P<servicename_sender>[^>]*)>)?(.*to=<(?P<servicename_recipient>[^>]*))?(, [^=]*=[^=]*=(?P<servicename_bool_saslauth>[^@]*))?')

    def _edit_results(self, results):
        # we remove the stuff we are not interested about
        del results['client']
        del results['ip']
        del results['reason']


        # then we will concat connect and disconnect
        if results['servicename_connect'] is not None or results['servicename_disconnect'] is not None:
            final = results['servicename_connect']
            if final is None:
                final = results['servicename_disconnect']

            results['servicename_communication'] = final

        del results['servicename_connect']
        del results['servicename_disconnect']

        # extract the country from which the email came from.
        # As you can see here doing such things as that is very easy.
        if results['servicename_sender'] is not None:
            results['servicename_sender'] = results['servicename_sender'].split('.')[-1]
        else:
            del results['servicename_sender']

        if results['servicename_recipient'] is not None:
            results['servicename_recipient'] = results['servicename_recipient'].split('@')[-1]
        else:
            del results['servicename_recipient']

        if results['servicename_bool_saslauth'] is None:
            if results['queueid'] is None:
                del results['servicename_bool_saslauth']

        del results['queueid']
