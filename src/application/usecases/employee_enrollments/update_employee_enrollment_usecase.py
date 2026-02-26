from typing import Any, Dict

from application.dtos import UpdateEmployeeEnrollmentDTO
from application.exceptions import BadRequestError, ConflictError
from application.repositories import RepositoryManagerInterface
from domain import EmployeeEnrollment

from .find_employee_enrollment_by_id_usecase import FindEmployeeEnrollmentByIdUseCase


class UpdateEmployeeEnrollmentUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.employee_enrollment_repository = (
            repository_manager.employee_enrollment_repository()
        )
        self.find_by_id_usecase = FindEmployeeEnrollmentByIdUseCase(repository_manager)

    def execute(
        self, enrollment_id: int, tenant_id: int, data: UpdateEmployeeEnrollmentDTO
    ) -> EmployeeEnrollment:
        enrollment = self.find_by_id_usecase.execute(
            enrollment_id=enrollment_id,
            raise_if_is_none=True,
        )

        if enrollment.tenant_id != tenant_id:
            raise BadRequestError("Enrollment does not belong to tenant.")

        data_to_update: Dict[str, Any] = {}

        if data.employee_id is not None:
            data_to_update["employee_id"] = data.employee_id

        if data.enrollment_code is not None:
            new_code = data.enrollment_code.strip()
            if len(new_code) == 0:
                raise BadRequestError("Enrollment code is required.")
            if new_code != enrollment.enrollment_code:
                existing = self.employee_enrollment_repository.find_by_code(
                    tenant_id=enrollment.tenant_id,
                    enrollment_code=new_code,
                )
                if existing is not None and existing.id != enrollment.id:
                    raise ConflictError("Enrollment code already exists for this tenant.")
            data_to_update["enrollment_code"] = new_code

        candidate_active_from = data.active_from or enrollment.active_from
        candidate_active_to = data.active_to if data.active_to is not None else enrollment.active_to
        if candidate_active_to is not None and candidate_active_to < candidate_active_from:
            raise BadRequestError("active_to must be greater than or equal to active_from.")

        if data.active_from is not None:
            data_to_update["active_from"] = data.active_from

        if data.active_to is not None:
            data_to_update["active_to"] = data.active_to

        if data.is_active is not None:
            data_to_update["is_active"] = data.is_active

        if len(data_to_update) == 0:
            return enrollment

        updated = self.employee_enrollment_repository.update(enrollment_id, data_to_update)
        if updated is None:
            raise BadRequestError("Unable to update enrollment.")
        return updated
