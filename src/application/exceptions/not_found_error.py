from http import HTTPStatus

from .api_error import APIError


class NotFoundError(Exception):
    def __init__(self, message: str):
        raise APIError(HTTPStatus.NOT_FOUND, message)
