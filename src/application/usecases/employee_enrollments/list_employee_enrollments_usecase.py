from application.dtos import ListEmployeeEnrollmentsDTO, PaginatedResult
from application.repositories import RepositoryManagerInterface
from domain import EmployeeEnrollment


class ListEmployeeEnrollmentsUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.employee_enrollment_repository = (
            repository_manager.employee_enrollment_repository()
        )

    def execute(self, data: ListEmployeeEnrollmentsDTO) -> PaginatedResult[EmployeeEnrollment]:
        result = self.employee_enrollment_repository.find_all(
            page=data.page,
            per_page=data.per_page,
            tenant_id=data.tenant_id,
            employee_id=data.employee_id,
            enrollment_code=data.enrollment_code,
            is_active=data.is_active,
        )
        return PaginatedResult(data=result.data, count=result.total_count, page=data.page)
