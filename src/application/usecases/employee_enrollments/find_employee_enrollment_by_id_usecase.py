from typing import Literal, Optional, overload

from application.exceptions import NotFoundError
from application.repositories import RepositoryManagerInterface
from domain import EmployeeEnrollment


class FindEmployeeEnrollmentByIdUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.employee_enrollment_repository = (
            repository_manager.employee_enrollment_repository()
        )

    @overload
    def execute(self, enrollment_id: int) -> Optional[EmployeeEnrollment]:
        pass

    @overload
    def execute(
        self, enrollment_id: int, raise_if_is_none: Literal[True]
    ) -> EmployeeEnrollment:
        pass

    @overload
    def execute(
        self, enrollment_id: int, raise_if_is_none: Literal[False]
    ) -> Optional[EmployeeEnrollment]:
        pass

    def execute(self, enrollment_id: int, raise_if_is_none: bool = False):
        enrollment = self.employee_enrollment_repository.find_by_id(enrollment_id)
        if raise_if_is_none and enrollment is None:
            raise NotFoundError("Employee enrollment not found.")
        return enrollment
