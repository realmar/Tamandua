""""""


class ExpressionInvalid(Exception):
    """Thrown when a given expression is invalid."""

    def __init__(self, details):
        super().__init__("The given expression is invalid: " + details)