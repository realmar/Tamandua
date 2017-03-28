"""Custom Exceptions used by the Application."""


class NoSubscriptionRegex(Exception):
    def __init__(self, clsname):
        super().__init__("No subscription regex defined in: " + clsname)


class NoDataRegex(Exception):
    def __init__(self, clsname):
        super().__init__("No data regex defined in: " + clsname)


class RegexGroupsMissing(Exception):
    def __init__(self, clsname, pattern):
        super().__init__("No named regex groups defined in: " + clsname + " pattern: " + pattern)


class MissingConfigField(Exception):
    def __init__(self, field):
        super().__init__("The following field is missing from the config: " + field)
