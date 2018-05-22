"""Module which contains exceptions raised by the web-app: backend."""

errors = {
    'ExpressionInvalid': {
        'message': 'The given expression is invalid',
        'status': 400
    },
    'MissingFields': {
        'message': 'The given request is missing fields.',
        'status': 400
    },
    'InvalidFieldValues': {
        'message': 'The given request contains invalid field values.',
        'status': 400
    }
}


class MissingFields(Exception):
    """Exception thrown when fields are missing from a request."""

    def __init__(self, *missing_fields: str) -> None:
        super().__init__('Following fields are missing: ' + ' '.join(missing_fields))


class InvalidFieldValues(Exception):
    """Exception thrown when fields contain invalid values."""

    def __init__(self, *invalid_fields: str) -> None:
        super().__init__('Following fields are invalid: ' + ''.join(invalid_fields))
