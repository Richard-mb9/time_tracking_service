from application.exceptions import BadRequestError
from application.repositories import RepositoryManagerInterface

from .find_enrollment_policy_assignment_by_id_usecase import (
    FindEnrollmentPolicyAssignmentByIdUseCase,
)


class DeleteEnrollmentPolicyAssignmentUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.enrollment_policy_assignment_repository = (
            repository_manager.enrollment_policy_assignment_repository()
        )
        self.find_assignment_by_id = FindEnrollmentPolicyAssignmentByIdUseCase(
            repository_manager
        )

    def execute(self, assignment_id: int, tenant_id: int) -> None:
        assignment = self.find_assignment_by_id.execute(
            assignment_id=assignment_id,
            raise_if_is_none=True,
        )
        if assignment.tenant_id != tenant_id:
            raise BadRequestError("Assignment does not belong to tenant.")
        self.enrollment_policy_assignment_repository.delete(assignment_id)
