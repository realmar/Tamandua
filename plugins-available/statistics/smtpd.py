"""Smtpd statistics plugin."""

import re

from src.plugins.bases.plugin_base import PluginBase


class Smtpd(PluginBase):
    """Smtpd statistics plugin."""

    def _define_subscription_regex(self):
        self._subscriptionRegex = re.compile(' postfix\/smtpd')

    def _define_data_regex(self):
        self._dataRegex = [
            re.compile(r'(?P<servicename_hostname_connection>(dis)?connect )'),
            re.compile(r'''
                client=(?P<servicename_hostname_client>[^\[]*)
                \[
                (?P<servicename_hostname_clientip>[^\]]*)
                (
                    \],\s
                    sasl_method=(?P<servicename_hostname_saslmethod>[^,]*)
                    ,\s
                    sasl_username=(?P<servicename_hostname_saslauth_BOOL>[^\n]*)
                )?
                ''', re.X),
            re.compile(r'(?P<servicename_hostname_action>hold|reject):'),
        ]

    def _edit_results(self, results):
        # currently we dont want the client in our statistic

        try:
            del results['servicename_hostname_client']
            del results['servicename_hostname_clientip']
        except Exception as e:
            pass
