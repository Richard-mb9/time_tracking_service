from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .holiday_calendar import HolidayCalendar


class Holiday:
    id: int
    holiday_calendar_id: int
    date: "date"
    name: str

    holiday_calendar: "HolidayCalendar"

    def __init__(self, holiday_calendar_id: int, date: "date", name: str):
        self.holiday_calendar_id = holiday_calendar_id
        self.date = date
        self.name = name
