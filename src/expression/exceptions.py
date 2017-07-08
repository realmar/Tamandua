""""""


class ExpressionInvalid(Exception):
    def __init__(self, details):
        super().__init__("The given expression is invalid: " + details)