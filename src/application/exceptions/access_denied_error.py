from http import HTTPStatus

from .api_error import APIError


class AccessDeniedError(Exception):
    def __init__(self, message: str):
        raise APIError(HTTPStatus.FORBIDDEN, message)
