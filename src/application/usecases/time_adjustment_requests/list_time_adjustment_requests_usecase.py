from application.dtos import ListTimeAdjustmentRequestsDTO, PaginatedResult
from application.repositories import RepositoryManagerInterface
from domain import TimeAdjustmentRequest


class ListTimeAdjustmentRequestsUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.time_adjustment_request_repository = (
            repository_manager.time_adjustment_request_repository()
        )

    def execute(
        self, data: ListTimeAdjustmentRequestsDTO
    ) -> PaginatedResult[TimeAdjustmentRequest]:
        result = self.time_adjustment_request_repository.find_all(
            page=data.page,
            per_page=data.per_page,
            tenant_id=data.tenant_id,
            enrollment_id=data.enrollment_id,
            status=data.status,
            start_date=data.start_date,
            end_date=data.end_date,
        )
        return PaginatedResult(data=result.data, count=result.total_count, page=data.page)
