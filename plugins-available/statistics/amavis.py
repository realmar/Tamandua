"""Amavis statistics plugin."""

import re

from src.plugins.bases.plugin_base import PluginBase


class Amavis(PluginBase):
    """Amavis statistics plugin."""

    def _define_subscription_regex(self):
        self._subscriptionRegex = re.compile(' amavis\[')

    def _define_data_regex(self):
        self._dataRegex = [
            re.compile(r'\) (?P<servicename_virus>[\w ]*)\ ')
        ]
