from datetime import date
from typing import Any, Dict, Optional

from application.dtos import UpdateEnrollmentPolicyAssignmentDTO
from application.exceptions import BadRequestError, ConflictError
from application.repositories import RepositoryManagerInterface
from application.usecases.work_policy_templates import FindWorkPolicyTemplateByIdUseCase
from domain import EnrollmentPolicyAssignment

from .find_enrollment_policy_assignment_by_id_usecase import (
    FindEnrollmentPolicyAssignmentByIdUseCase,
)


class UpdateEnrollmentPolicyAssignmentUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.enrollment_policy_assignment_repository = (
            repository_manager.enrollment_policy_assignment_repository()
        )
        self.find_assignment_by_id = FindEnrollmentPolicyAssignmentByIdUseCase(
            repository_manager
        )
        self.find_template_by_id = FindWorkPolicyTemplateByIdUseCase(repository_manager)

    def execute(
        self,
        assignment_id: int,
        tenant_id: int,
        data: UpdateEnrollmentPolicyAssignmentDTO,
    ) -> EnrollmentPolicyAssignment:
        assignment = self.find_assignment_by_id.execute(
            assignment_id=assignment_id,
            raise_if_is_none=True,
        )

        if assignment.tenant_id != tenant_id:
            raise BadRequestError("Assignment does not belong to tenant.")

        data_to_update: Dict[str, Any] = {}

        if data.template_id is not None:
            template = self.find_template_by_id.execute(
                template_id=data.template_id,
                raise_if_is_none=True,
            )
            if template.tenant_id != tenant_id:
                raise BadRequestError("Template does not belong to tenant.")
            data_to_update["template_id"] = data.template_id

        candidate_effective_from = (
            data.effective_from if data.effective_from is not None else assignment.effective_from
        )
        candidate_effective_to = (
            data.effective_to if data.effective_to is not None else assignment.effective_to
        )

        self.__validate_period(candidate_effective_from, candidate_effective_to)

        overlapping = self.enrollment_policy_assignment_repository.find_overlapping(
            employee_id=assignment.employee_id,
            matricula=assignment.matricula,
            effective_from=candidate_effective_from,
            effective_to=candidate_effective_to,
            exclude_assignment_id=assignment.id,
        )
        if len(overlapping) > 0:
            raise ConflictError("Assignment period overlaps with an existing assignment.")

        if data.effective_from is not None:
            data_to_update["effective_from"] = data.effective_from

        if data.effective_to is not None:
            data_to_update["effective_to"] = data.effective_to

        if len(data_to_update) == 0:
            return assignment

        updated = self.enrollment_policy_assignment_repository.update(
            assignment_id=assignment_id,
            data=data_to_update,
        )
        if updated is None:
            raise BadRequestError("Unable to update assignment.")
        return updated

    def __validate_period(
        self, effective_from: date, effective_to: Optional[date]
    ) -> None:
        if effective_to is not None and effective_to < effective_from:
            raise BadRequestError("effective_to must be greater than or equal to effective_from.")
