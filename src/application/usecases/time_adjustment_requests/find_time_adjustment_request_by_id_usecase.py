from typing import Literal, Optional, overload

from application.exceptions import NotFoundError
from application.repositories import RepositoryManagerInterface
from domain import TimeAdjustmentRequest


class FindTimeAdjustmentRequestByIdUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.time_adjustment_request_repository = (
            repository_manager.time_adjustment_request_repository()
        )

    @overload
    def execute(self, request_id: int) -> Optional[TimeAdjustmentRequest]:
        pass

    @overload
    def execute(
        self, request_id: int, raise_if_is_none: Literal[True]
    ) -> TimeAdjustmentRequest:
        pass

    @overload
    def execute(
        self, request_id: int, raise_if_is_none: Literal[False]
    ) -> Optional[TimeAdjustmentRequest]:
        pass

    def execute(self, request_id: int, raise_if_is_none: bool = False):
        request = self.time_adjustment_request_repository.find_by_id(request_id)
        if raise_if_is_none and request is None:
            raise NotFoundError("Time adjustment request not found.")
        return request
