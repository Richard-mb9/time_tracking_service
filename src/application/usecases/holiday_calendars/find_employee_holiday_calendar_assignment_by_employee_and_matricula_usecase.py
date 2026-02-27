from typing import Literal, Optional, overload

from application.exceptions import NotFoundError
from application.repositories import RepositoryManagerInterface
from domain import EmployeeHolidayCalendarAssignment


class FindEmployeeHolidayCalendarAssignmentByEmployeeAndMatriculaUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.employee_holiday_calendar_assignment_repository = (
            repository_manager.employee_holiday_calendar_assignment_repository()
        )

    @overload
    def execute(
        self, employee_id: int, matricula: str, tenant_id: int
    ) -> Optional[EmployeeHolidayCalendarAssignment]:
        pass

    @overload
    def execute(
        self,
        employee_id: int,
        matricula: str,
        tenant_id: int,
        raise_if_is_none: Literal[True],
    ) -> EmployeeHolidayCalendarAssignment:
        pass

    @overload
    def execute(
        self,
        employee_id: int,
        matricula: str,
        tenant_id: int,
        raise_if_is_none: Literal[False],
    ) -> Optional[EmployeeHolidayCalendarAssignment]:
        pass

    def execute(
        self,
        employee_id: int,
        matricula: str,
        tenant_id: int,
        raise_if_is_none: bool = False,
    ):
        assignment = (
            self.employee_holiday_calendar_assignment_repository.find_by_employee_id_and_matricula_and_tenant_id(
                employee_id=employee_id,
                matricula=matricula,
                tenant_id=tenant_id,
            )
        )
        if raise_if_is_none and assignment is None:
            raise NotFoundError("Employee holiday calendar assignment not found.")
        return assignment
