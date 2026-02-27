from typing import List, Set, Tuple

from application.dtos import (
    CreateEnrollmentPolicyAssignmentDTO,
    CreateEnrollmentPolicyAssignmentsDTO,
)
from application.exceptions import BadRequestError
from application.repositories import RepositoryManagerInterface
from domain import EnrollmentPolicyAssignment

from .create_enrollment_policy_assignment_usecase import (
    CreateEnrollmentPolicyAssignmentUseCase,
)


class CreateEnrollmentPolicyAssignmentsUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.create_enrollment_policy_assignment_usecase = (
            CreateEnrollmentPolicyAssignmentUseCase(repository_manager)
        )

    def execute(
        self, data: CreateEnrollmentPolicyAssignmentsDTO
    ) -> List[EnrollmentPolicyAssignment]:
        if len(data.employees) == 0:
            raise BadRequestError("employees list is required.")

        assignments: List[EnrollmentPolicyAssignment] = []
        processed: Set[Tuple[int, str]] = set()

        for item in data.employees:
            matricula = item.matricula.strip()
            dedup_key = (item.employee_id, matricula)
            if dedup_key in processed:
                raise BadRequestError(
                    "Duplicated employeeId and matricula in employees list."
                )
            processed.add(dedup_key)

            assignment = self.create_enrollment_policy_assignment_usecase.execute(
                CreateEnrollmentPolicyAssignmentDTO(
                    tenant_id=data.tenant_id,
                    employee_id=item.employee_id,
                    matricula=matricula,
                    template_id=data.template_id,
                    effective_from=data.effective_from,
                    effective_to=data.effective_to,
                )
            )
            assignments.append(assignment)

        return assignments
