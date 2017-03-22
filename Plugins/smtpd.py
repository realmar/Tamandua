"""Smtpd statistics plugin."""

from lib.plugin_base import PluginBase
import re


class Smtpd(PluginBase):
    """Smtpd statistics plugin."""

    def _define_subscription_regex(self):
        self._subscriptionRegex = re.compile(' postfix\/smtpd')

    def _define_data_regex(self):
        self._dataRegex = [
            re.compile(r'(?P<servicename_hostname_connection>(dis)?connect )'),
            re.compile(r'''
                    sasl_method=(?P<servicename_hostname_saslmethod>[^,]*),\s
                    sasl_username=(?P<servicename_hostname_bool_saslauth>[^\n]*)
                    ''', re.X),
            re.compile(r'(?P<servicename_hostname_action>hold|reject):'),
        ]
