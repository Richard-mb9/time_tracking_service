from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Dict, Optional

from application.repositories.types import DBPaginatedResult
from domain import HolidayCalendar


class HolidayCalendarRepositoryInterface(ABC):
    @abstractmethod
    def create(self, holiday_calendar: HolidayCalendar) -> HolidayCalendar:
        raise NotImplementedError

    @abstractmethod
    def update(
        self, holiday_calendar_id: int, data: Dict[str, Any]
    ) -> Optional[HolidayCalendar]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, holiday_calendar_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, holiday_calendar_id: int) -> Optional[HolidayCalendar]:
        raise NotImplementedError

    @abstractmethod
    def find_by_name(
        self, tenant_id: int, name: str
    ) -> Optional[HolidayCalendar]:
        raise NotImplementedError

    @abstractmethod
    def find_all(
        self,
        page: int,
        per_page: int,
        tenant_id: Optional[int] = None,
        name: Optional[str] = None,
        city: Optional[str] = None,
        uf: Optional[str] = None,
    ) -> DBPaginatedResult[HolidayCalendar]:
        raise NotImplementedError

    @abstractmethod
    def has_holiday_on_date(self, holiday_calendar_id: int, holiday_date: date) -> bool:
        raise NotImplementedError
