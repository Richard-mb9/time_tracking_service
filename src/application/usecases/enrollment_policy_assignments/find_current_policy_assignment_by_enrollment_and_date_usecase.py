from datetime import date
from typing import Optional

from application.repositories import RepositoryManagerInterface
from domain import EnrollmentPolicyAssignment


class FindCurrentPolicyAssignmentByEnrollmentAndDateUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.enrollment_policy_assignment_repository = (
            repository_manager.enrollment_policy_assignment_repository()
        )

    def execute(
        self, employee_id: int, matricula: str, reference_date: date
    ) -> Optional[EnrollmentPolicyAssignment]:
        return self.enrollment_policy_assignment_repository.find_current_by_employee_and_matricula_and_date(
            employee_id=employee_id,
            matricula=matricula,
            reference_date=reference_date,
        )
