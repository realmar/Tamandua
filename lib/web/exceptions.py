"""Module which contains exceptions raised by the web-app: backend."""


class ExpressionInvalid(Exception):
    def __init__(self, details):
        super().__init__("The given expression is invalid: " + details)