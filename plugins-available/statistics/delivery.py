"""Delivery statistics."""

import re

from src.plugins.bases.plugin_base import PluginBase


class Smtp(PluginBase):
    """Smtp delivery statistics plugin."""

    def _define_subscription_regex(self):
        self._subscriptionRegex = re.compile('postfix\/smtp\[')

    def _define_data_regex(self):
        self._dataRegex = [
            re.compile('status=(?P<delivery_extern_status>[^\ ]*)')
        ]


class Local(PluginBase):
    """Local delivery statistics plugin."""

    def _define_subscription_regex(self):
        self._subscriptionRegex = re.compile('postfix\/local\[')

    def _define_data_regex(self):
        self._dataRegex = [
            re.compile('status=(?P<delivery_intern_status>[^\ ]*)')
        ]
