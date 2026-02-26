from http import HTTPStatus

from .api_error import APIError


class LockedError(Exception):
    def __init__(self, message: str):
        raise APIError(HTTPStatus.LOCKED, message)
