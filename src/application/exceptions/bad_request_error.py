from http import HTTPStatus

from .api_error import APIError


class BadRequestError(Exception):
    def __init__(self, message: str):
        raise APIError(HTTPStatus.BAD_REQUEST, message)
