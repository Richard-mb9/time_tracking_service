from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from domain import EmployeeHolidayCalendarAssignment


class EmployeeHolidayCalendarAssignmentRepositoryInterface(ABC):
    @abstractmethod
    def create(
        self, assignment: EmployeeHolidayCalendarAssignment
    ) -> EmployeeHolidayCalendarAssignment:
        raise NotImplementedError

    @abstractmethod
    def update(
        self, assignment_id: int, data: Dict[str, Any]
    ) -> Optional[EmployeeHolidayCalendarAssignment]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, assignment_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(
        self, assignment_id: int
    ) -> Optional[EmployeeHolidayCalendarAssignment]:
        raise NotImplementedError

    @abstractmethod
    def find_by_employee_id_and_matricula_and_tenant_id(
        self, employee_id: int, matricula: str, tenant_id: int
    ) -> Optional[EmployeeHolidayCalendarAssignment]:
        raise NotImplementedError
