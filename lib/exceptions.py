"""Custom Exceptions used by the Application."""

class NoMatch(Exception):
    def __init__(self):
        super().__init__("The given line did not match with the plugin.")
