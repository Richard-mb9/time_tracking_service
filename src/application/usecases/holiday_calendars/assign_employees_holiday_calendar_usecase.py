from typing import List, Set, Tuple

from application.dtos import (
    AssignEmployeeHolidayCalendarDTO,
    AssignEmployeesHolidayCalendarDTO,
)
from application.exceptions import BadRequestError
from application.repositories import RepositoryManagerInterface
from domain import EmployeeHolidayCalendarAssignment

from .assign_employee_holiday_calendar_usecase import AssignEmployeeHolidayCalendarUseCase


class AssignEmployeesHolidayCalendarUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.assign_employee_holiday_calendar_usecase = AssignEmployeeHolidayCalendarUseCase(
            repository_manager
        )

    def execute(
        self, data: AssignEmployeesHolidayCalendarDTO
    ) -> List[EmployeeHolidayCalendarAssignment]:
        if len(data.employees) == 0:
            raise BadRequestError("employees list is required.")

        assignments: List[EmployeeHolidayCalendarAssignment] = []
        processed: Set[Tuple[int, str]] = set()

        for employee in data.employees:
            matricula = employee.matricula.strip()
            dedup_key = (employee.employee_id, matricula)
            if dedup_key in processed:
                raise BadRequestError(
                    "Duplicated employeeId and matricula in employees list."
                )
            processed.add(dedup_key)

            assignment = self.assign_employee_holiday_calendar_usecase.execute(
                AssignEmployeeHolidayCalendarDTO(
                    tenant_id=data.tenant_id,
                    employee_id=employee.employee_id,
                    matricula=matricula,
                    holiday_calendar_id=data.holiday_calendar_id,
                )
            )
            assignments.append(assignment)

        return assignments
