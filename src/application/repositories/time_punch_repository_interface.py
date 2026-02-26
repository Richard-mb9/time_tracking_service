from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from application.repositories.types import DBPaginatedResult
from domain import TimePunch
from domain.enums import PunchType


class TimePunchRepositoryInterface(ABC):
    @abstractmethod
    def create(self, punch: TimePunch) -> TimePunch:
        raise NotImplementedError

    @abstractmethod
    def update(self, punch_id: int, data: Dict[str, Any]) -> Optional[TimePunch]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, punch_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, punch_id: int) -> Optional[TimePunch]:
        raise NotImplementedError

    @abstractmethod
    def find_duplicate(
        self, employee_id: int, matricula: str, punched_at: datetime, punch_type: PunchType
    ) -> Optional[TimePunch]:
        raise NotImplementedError

    @abstractmethod
    def find_last_by_employee_and_matricula(
        self, employee_id: int, matricula: str
    ) -> Optional[TimePunch]:
        raise NotImplementedError

    @abstractmethod
    def find_by_employee_and_matricula_and_period(
        self, employee_id: int, matricula: str, start_at: datetime, end_at: datetime
    ) -> List[TimePunch]:
        raise NotImplementedError

    @abstractmethod
    def find_by_employee_and_matricula_and_date(
        self, employee_id: int, matricula: str, work_date: date
    ) -> List[TimePunch]:
        raise NotImplementedError

    @abstractmethod
    def find_other_matriculas_with_punch_on_date(
        self,
        tenant_id: int,
        employee_id: int,
        work_date: date,
        matricula_to_exclude: str,
    ) -> List[TimePunch]:
        raise NotImplementedError

    @abstractmethod
    def find_all(
        self,
        page: int,
        per_page: int,
        tenant_id: Optional[int] = None,
        employee_id: Optional[int] = None,
        matricula: Optional[str] = None,
        start_at: Optional[datetime] = None,
        end_at: Optional[datetime] = None,
        punch_type: Optional[PunchType] = None,
    ) -> DBPaginatedResult[TimePunch]:
        raise NotImplementedError
