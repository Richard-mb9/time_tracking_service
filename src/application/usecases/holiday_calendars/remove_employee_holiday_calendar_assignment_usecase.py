from application.repositories import RepositoryManagerInterface

from .find_employee_holiday_calendar_assignment_by_employee_id_usecase import (
    FindEmployeeHolidayCalendarAssignmentByEmployeeIdUseCase,
)


class RemoveEmployeeHolidayCalendarAssignmentUseCase:
    def __init__(self, repository_manager: RepositoryManagerInterface):
        self.employee_holiday_calendar_assignment_repository = (
            repository_manager.employee_holiday_calendar_assignment_repository()
        )
        self.find_assignment_by_employee_id_usecase = (
            FindEmployeeHolidayCalendarAssignmentByEmployeeIdUseCase(repository_manager)
        )

    def execute(self, employee_id: int, tenant_id: int) -> None:
        assignment = self.find_assignment_by_employee_id_usecase.execute(
            employee_id=employee_id,
            tenant_id=tenant_id,
            raise_if_is_none=True,
        )
        self.employee_holiday_calendar_assignment_repository.delete(assignment.id)
