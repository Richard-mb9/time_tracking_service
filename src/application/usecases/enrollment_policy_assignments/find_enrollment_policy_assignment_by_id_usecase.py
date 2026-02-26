from typing import Literal, Optional, overload

from application.exceptions import NotFoundError
from application.repositories import RepositoryManagerInterface
from domain import EnrollmentPolicyAssignment


class FindEnrollmentPolicyAssignmentByIdUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.enrollment_policy_assignment_repository = (
            repository_manager.enrollment_policy_assignment_repository()
        )

    @overload
    def execute(self, assignment_id: int) -> Optional[EnrollmentPolicyAssignment]:
        pass

    @overload
    def execute(
        self, assignment_id: int, raise_if_is_none: Literal[True]
    ) -> EnrollmentPolicyAssignment:
        pass

    @overload
    def execute(
        self, assignment_id: int, raise_if_is_none: Literal[False]
    ) -> Optional[EnrollmentPolicyAssignment]:
        pass

    def execute(self, assignment_id: int, raise_if_is_none: bool = False):
        assignment = self.enrollment_policy_assignment_repository.find_by_id(assignment_id)
        if raise_if_is_none and assignment is None:
            raise NotFoundError("Enrollment policy assignment not found.")
        return assignment
