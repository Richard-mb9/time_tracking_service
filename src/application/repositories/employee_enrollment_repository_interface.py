from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Dict, List, Optional

from application.repositories.types import DBPaginatedResult
from domain import EmployeeEnrollment


class EmployeeEnrollmentRepositoryInterface(ABC):
    @abstractmethod
    def create(self, enrollment: EmployeeEnrollment) -> EmployeeEnrollment:
        raise NotImplementedError

    @abstractmethod
    def update(
        self, enrollment_id: int, data: Dict[str, Any]
    ) -> Optional[EmployeeEnrollment]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, enrollment_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, enrollment_id: int) -> Optional[EmployeeEnrollment]:
        raise NotImplementedError

    @abstractmethod
    def find_by_code(
        self, tenant_id: int, enrollment_code: str
    ) -> Optional[EmployeeEnrollment]:
        raise NotImplementedError

    @abstractmethod
    def find_all(
        self,
        page: int,
        per_page: int,
        tenant_id: Optional[int] = None,
        employee_id: Optional[int] = None,
        enrollment_code: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> DBPaginatedResult[EmployeeEnrollment]:
        raise NotImplementedError

    @abstractmethod
    def find_other_enrollments_with_punch_on_date(
        self,
        tenant_id: int,
        employee_id: int,
        work_date: date,
        exclude_enrollment_id: int,
    ) -> List[EmployeeEnrollment]:
        raise NotImplementedError
