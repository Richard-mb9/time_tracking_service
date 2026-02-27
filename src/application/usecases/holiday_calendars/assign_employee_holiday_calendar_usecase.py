from application.dtos import AssignEmployeeHolidayCalendarDTO
from application.exceptions import BadRequestError
from application.repositories import RepositoryManagerInterface
from domain import EmployeeHolidayCalendarAssignment

from .find_employee_holiday_calendar_assignment_by_employee_id_usecase import (
    FindEmployeeHolidayCalendarAssignmentByEmployeeIdUseCase,
)
from .find_holiday_calendar_by_id_usecase import FindHolidayCalendarByIdUseCase


class AssignEmployeeHolidayCalendarUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.employee_holiday_calendar_assignment_repository = (
            repository_manager.employee_holiday_calendar_assignment_repository()
        )
        self.find_holiday_calendar_by_id_usecase = FindHolidayCalendarByIdUseCase(
            repository_manager
        )
        self.find_assignment_by_employee_id_usecase = (
            FindEmployeeHolidayCalendarAssignmentByEmployeeIdUseCase(repository_manager)
        )

    def execute(
        self, data: AssignEmployeeHolidayCalendarDTO
    ) -> EmployeeHolidayCalendarAssignment:
        holiday_calendar = self.find_holiday_calendar_by_id_usecase.execute(
            holiday_calendar_id=data.holiday_calendar_id,
            raise_if_is_none=True,
        )
        if holiday_calendar.tenant_id != data.tenant_id:
            raise BadRequestError("Holiday calendar does not belong to tenant.")

        existing_assignment = self.find_assignment_by_employee_id_usecase.execute(
            employee_id=data.employee_id,
            tenant_id=data.tenant_id,
        )
        if existing_assignment is None:
            return self.employee_holiday_calendar_assignment_repository.create(
                EmployeeHolidayCalendarAssignment(
                    employee_id=data.employee_id,
                    holiday_calendar_id=data.holiday_calendar_id,
                )
            )

        if existing_assignment.holiday_calendar_id == data.holiday_calendar_id:
            return existing_assignment

        updated = self.employee_holiday_calendar_assignment_repository.update(
            assignment_id=existing_assignment.id,
            data={"holiday_calendar_id": data.holiday_calendar_id},
        )
        if updated is None:
            raise BadRequestError("Unable to assign holiday calendar to employee.")
        return updated
