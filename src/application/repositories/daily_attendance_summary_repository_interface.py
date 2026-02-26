from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

from application.repositories.types import DBPaginatedResult
from domain import DailyAttendanceSummary
from domain.enums import DailyAttendanceStatus


class DailyAttendanceSummaryRepositoryInterface(ABC):
    @abstractmethod
    def upsert(self, summary: DailyAttendanceSummary) -> DailyAttendanceSummary:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, summary_id: int) -> Optional[DailyAttendanceSummary]:
        raise NotImplementedError

    @abstractmethod
    def find_by_employee_and_matricula_and_date(
        self, employee_id: int, matricula: str, work_date: date
    ) -> Optional[DailyAttendanceSummary]:
        raise NotImplementedError

    @abstractmethod
    def find_all(
        self,
        page: int,
        per_page: int,
        tenant_id: Optional[int] = None,
        employee_id: Optional[int] = None,
        matricula: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[DailyAttendanceStatus] = None,
    ) -> DBPaginatedResult[DailyAttendanceSummary]:
        raise NotImplementedError
