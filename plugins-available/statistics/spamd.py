"""Spamd statistics plugin."""

import re

from src.plugins.bases.plugin_base import PluginBase


class Spamd(PluginBase):
    """Spamd statistics plugin."""

    def _define_subscription_regex(self):
        self._subscriptionRegex = re.compile(' spamd\[')

    def _define_data_regex(self):
        self._dataRegex = [
            re.compile(r'spamd: (?P<servicename>(clean message|identified spam)) \(')
            ]
