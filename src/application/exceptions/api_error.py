from http import HTTPStatus


class APIError(Exception):
    def __init__(self, status_code: HTTPStatus, message: str):
        super().__init__()
        self.status_code = status_code
        self.message = message
