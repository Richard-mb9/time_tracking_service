from application.exceptions import BadRequestError
from application.repositories import RepositoryManagerInterface

from .find_employee_enrollment_by_id_usecase import FindEmployeeEnrollmentByIdUseCase


class DeleteEmployeeEnrollmentUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.employee_enrollment_repository = (
            repository_manager.employee_enrollment_repository()
        )
        self.find_by_id_usecase = FindEmployeeEnrollmentByIdUseCase(repository_manager)

    def execute(self, enrollment_id: int, tenant_id: int) -> None:
        enrollment = self.find_by_id_usecase.execute(
            enrollment_id=enrollment_id,
            raise_if_is_none=True,
        )
        if enrollment.tenant_id != tenant_id:
            raise BadRequestError("Enrollment does not belong to tenant.")
        self.employee_enrollment_repository.delete(enrollment_id)
