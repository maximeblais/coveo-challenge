from http import HTTPStatus


# Custom exception for invalid queries
class InvalidQuery(Exception):
    # Default status code assuming bad request
    status_code = HTTPStatus.BAD_REQUEST

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        result = dict(self.payload or ())
        result['message'] = self.message
        return result
