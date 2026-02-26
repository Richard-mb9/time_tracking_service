from http import HTTPStatus

from .api_error import APIError


class UnprocessableEntityError(Exception):
    def __init__(self, message: str):
        raise APIError(HTTPStatus.UNPROCESSABLE_ENTITY, message)
