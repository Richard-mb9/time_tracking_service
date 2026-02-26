from application.dtos import ListEnrollmentPolicyAssignmentsDTO, PaginatedResult
from application.repositories import RepositoryManagerInterface
from domain import EnrollmentPolicyAssignment


class ListEnrollmentPolicyAssignmentsUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.enrollment_policy_assignment_repository = (
            repository_manager.enrollment_policy_assignment_repository()
        )

    def execute(
        self, data: ListEnrollmentPolicyAssignmentsDTO
    ) -> PaginatedResult[EnrollmentPolicyAssignment]:
        result = self.enrollment_policy_assignment_repository.find_all(
            page=data.page,
            per_page=data.per_page,
            tenant_id=data.tenant_id,
            employee_id=data.employee_id,
            matricula=data.matricula,
            template_id=data.template_id,
            target_date=data.target_date,
        )
        return PaginatedResult(data=result.data, count=result.total_count, page=data.page)
