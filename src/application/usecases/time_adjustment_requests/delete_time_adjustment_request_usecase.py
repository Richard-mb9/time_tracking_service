from application.exceptions import BadRequestError
from application.repositories import RepositoryManagerInterface
from domain.enums import TimeAdjustmentStatus

from .find_time_adjustment_request_by_id_usecase import FindTimeAdjustmentRequestByIdUseCase


class DeleteTimeAdjustmentRequestUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.time_adjustment_request_repository = (
            repository_manager.time_adjustment_request_repository()
        )
        self.time_adjustment_item_repository = (
            repository_manager.time_adjustment_item_repository()
        )
        self.find_request_by_id = FindTimeAdjustmentRequestByIdUseCase(repository_manager)

    def execute(self, request_id: int, tenant_id: int) -> None:
        request = self.find_request_by_id.execute(
            request_id=request_id,
            raise_if_is_none=True,
        )

        if request.tenant_id != tenant_id:
            raise BadRequestError("Request does not belong to tenant.")

        if request.status != TimeAdjustmentStatus.PENDING:
            raise BadRequestError("Only pending requests can be cancelled.")

        self.time_adjustment_item_repository.delete_by_request_id(request_id)
        self.time_adjustment_request_repository.delete(request_id)
