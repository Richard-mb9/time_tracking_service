from datetime import date
from typing import Any, Dict, Optional

from application.repositories import HolidayCalendarRepositoryInterface
from application.repositories.types import DBPaginatedResult
from domain import Holiday, HolidayCalendar
from infra.database_manager import DatabaseManagerConnection


class HolidayCalendarRepository(HolidayCalendarRepositoryInterface):
    def __init__(self, db_manager: DatabaseManagerConnection):
        self.session = db_manager.session

    def create(self, holiday_calendar: HolidayCalendar) -> HolidayCalendar:
        self.session.add(holiday_calendar)
        self.session.commit()
        self.session.refresh(holiday_calendar)
        return holiday_calendar

    def update(
        self, holiday_calendar_id: int, data: Dict[str, Any]
    ) -> Optional[HolidayCalendar]:
        holiday_calendar = self.find_by_id(holiday_calendar_id)
        if holiday_calendar is None:
            return None

        for key, value in data.items():
            setattr(holiday_calendar, key, value)

        self.session.commit()
        self.session.refresh(holiday_calendar)
        return holiday_calendar

    def delete(self, holiday_calendar_id: int) -> None:
        holiday_calendar = self.find_by_id(holiday_calendar_id)
        if holiday_calendar is None:
            return
        self.session.delete(holiday_calendar)
        self.session.commit()

    def find_by_id(self, holiday_calendar_id: int) -> Optional[HolidayCalendar]:
        return (
            self.session.query(HolidayCalendar)
            .filter(HolidayCalendar.id == holiday_calendar_id)
            .first()
        )

    def find_by_name(self, tenant_id: int, name: str) -> Optional[HolidayCalendar]:
        return (
            self.session.query(HolidayCalendar)
            .filter(HolidayCalendar.tenant_id == tenant_id)
            .filter(HolidayCalendar.name == name)
            .first()
        )

    def find_all(
        self,
        page: int,
        per_page: int,
        tenant_id: Optional[int] = None,
        name: Optional[str] = None,
        city: Optional[str] = None,
        uf: Optional[str] = None,
    ) -> DBPaginatedResult[HolidayCalendar]:
        query = self.session.query(HolidayCalendar)

        if tenant_id is not None:
            query = query.filter(HolidayCalendar.tenant_id == tenant_id)

        if name is not None:
            query = query.filter(HolidayCalendar.name.ilike(f"%{name}%"))

        if city is not None:
            query = query.filter(HolidayCalendar.city.ilike(f"%{city}%"))

        if uf is not None:
            query = query.filter(HolidayCalendar.uf == uf)

        total = query.count()
        data = (
            query.order_by(HolidayCalendar.id.asc())
            .offset(page * per_page)
            .limit(per_page)
            .all()
        )
        return DBPaginatedResult(data=data, total_count=total)

    def has_holiday_on_date(self, holiday_calendar_id: int, holiday_date: date) -> bool:
        holiday = (
            self.session.query(Holiday)
            .filter(Holiday.holiday_calendar_id == holiday_calendar_id)
            .filter(Holiday.date == holiday_date)
            .first()
        )
        return holiday is not None
