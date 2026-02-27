from typing import Any, Dict, Optional

from application.repositories import (
    EmployeeHolidayCalendarAssignmentRepositoryInterface,
)
from domain import EmployeeHolidayCalendarAssignment, HolidayCalendar
from infra.database_manager import DatabaseManagerConnection


class EmployeeHolidayCalendarAssignmentRepository(
    EmployeeHolidayCalendarAssignmentRepositoryInterface
):
    def __init__(self, db_manager: DatabaseManagerConnection):
        self.session = db_manager.session

    def create(
        self, assignment: EmployeeHolidayCalendarAssignment
    ) -> EmployeeHolidayCalendarAssignment:
        self.session.add(assignment)
        self.session.commit()
        self.session.refresh(assignment)
        return assignment

    def update(
        self, assignment_id: int, data: Dict[str, Any]
    ) -> Optional[EmployeeHolidayCalendarAssignment]:
        assignment = self.find_by_id(assignment_id)
        if assignment is None:
            return None

        for key, value in data.items():
            setattr(assignment, key, value)

        self.session.commit()
        self.session.refresh(assignment)
        return assignment

    def delete(self, assignment_id: int) -> None:
        assignment = self.find_by_id(assignment_id)
        if assignment is None:
            return
        self.session.delete(assignment)
        self.session.commit()

    def find_by_id(
        self, assignment_id: int
    ) -> Optional[EmployeeHolidayCalendarAssignment]:
        return (
            self.session.query(EmployeeHolidayCalendarAssignment)
            .filter(EmployeeHolidayCalendarAssignment.id == assignment_id)
            .first()
        )

    def find_by_employee_id_and_tenant_id(
        self, employee_id: int, tenant_id: int
    ) -> Optional[EmployeeHolidayCalendarAssignment]:
        return (
            self.session.query(EmployeeHolidayCalendarAssignment)
            .join(EmployeeHolidayCalendarAssignment.holiday_calendar)
            .filter(EmployeeHolidayCalendarAssignment.employee_id == employee_id)
            .filter(HolidayCalendar.tenant_id == tenant_id)
            .first()
        )
