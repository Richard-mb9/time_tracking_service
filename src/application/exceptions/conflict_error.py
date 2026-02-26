from http import HTTPStatus

from .api_error import APIError


class ConflictError(Exception):
    def __init__(self, message: str):
        raise APIError(HTTPStatus.CONFLICT, message)
