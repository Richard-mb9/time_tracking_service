from http import HTTPStatus

from .api_error import APIError


class UnauthorizedError(Exception):
    def __init__(self, message: str):
        raise APIError(HTTPStatus.UNAUTHORIZED, message)
