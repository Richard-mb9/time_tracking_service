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
        self, enrollment_id: int, punched_at: datetime, punch_type: PunchType
    ) -> Optional[TimePunch]:
        raise NotImplementedError

    @abstractmethod
    def find_last_by_enrollment(self, enrollment_id: int) -> Optional[TimePunch]:
        raise NotImplementedError

    @abstractmethod
    def find_by_enrollment_and_period(
        self, enrollment_id: int, start_at: datetime, end_at: datetime
    ) -> List[TimePunch]:
        raise NotImplementedError

    @abstractmethod
    def find_by_enrollment_and_date(
        self, enrollment_id: int, work_date: date
    ) -> List[TimePunch]:
        raise NotImplementedError

    @abstractmethod
    def find_all(
        self,
        page: int,
        per_page: int,
        tenant_id: Optional[int] = None,
        enrollment_id: Optional[int] = None,
        start_at: Optional[datetime] = None,
        end_at: Optional[datetime] = None,
        punch_type: Optional[PunchType] = None,
    ) -> DBPaginatedResult[TimePunch]:
        raise NotImplementedError
