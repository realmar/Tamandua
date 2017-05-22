"""Module which contains exceptions raised by the web-app: backend."""


from flask_restful import HTTPException


class ExpressionInvalid(HTTPException):
    def __init__(self, details):
        super().__init__("The given expression is invalid: " + details)


errors = {
    'ExpressionInvalid': {
        'status': 400
    }
}