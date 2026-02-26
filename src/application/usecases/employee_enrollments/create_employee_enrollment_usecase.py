from application.dtos import CreateEmployeeEnrollmentDTO
from application.exceptions import BadRequestError, ConflictError
from application.repositories import RepositoryManagerInterface
from domain import EmployeeEnrollment


class CreateEmployeeEnrollmentUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.employee_enrollment_repository = (
            repository_manager.employee_enrollment_repository()
        )

    def execute(self, data: CreateEmployeeEnrollmentDTO) -> EmployeeEnrollment:
        if len(data.enrollment_code.strip()) == 0:
            raise BadRequestError("Enrollment code is required.")

        if data.active_to is not None and data.active_to < data.active_from:
            raise BadRequestError("active_to must be greater than or equal to active_from.")

        existing = self.employee_enrollment_repository.find_by_code(
            tenant_id=data.tenant_id,
            enrollment_code=data.enrollment_code.strip(),
        )
        if existing is not None:
            raise ConflictError("Enrollment code already exists for this tenant.")

        enrollment = EmployeeEnrollment(
            tenant_id=data.tenant_id,
            employee_id=data.employee_id,
            enrollment_code=data.enrollment_code.strip(),
            active_from=data.active_from,
            active_to=data.active_to,
            is_active=data.is_active,
        )
        return self.employee_enrollment_repository.create(enrollment)
