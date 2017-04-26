"""Spamd statistics plugin."""

from lib.plugins.plugin_base import PluginBase
import re


class Spamd(PluginBase):
    """Spamd statistics plugin."""

    def _define_subscription_regex(self):
        self._subscriptionRegex = re.compile(' spamd\[')

    def _define_data_regex(self):
        self._dataRegex = [
            re.compile(r'spamd: (?P<servicename>(clean message|identified spam)) \(')
            ]
