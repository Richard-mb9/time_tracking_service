from application.dtos import ListTimePunchesDTO, PaginatedResult
from application.repositories import RepositoryManagerInterface
from domain import TimePunch


class ListTimePunchesUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.time_punch_repository = repository_manager.time_punch_repository()

    def execute(self, data: ListTimePunchesDTO) -> PaginatedResult[TimePunch]:
        result = self.time_punch_repository.find_all(
            page=data.page,
            per_page=data.per_page,
            tenant_id=data.tenant_id,
            employee_id=data.employee_id,
            matricula=data.matricula,
            start_at=data.start_at,
            end_at=data.end_at,
            punch_type=data.punch_type,
        )
        return PaginatedResult(data=result.data, count=result.total_count, page=data.page)
