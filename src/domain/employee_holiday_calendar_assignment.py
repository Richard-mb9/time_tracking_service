from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .holiday_calendar import HolidayCalendar


class EmployeeHolidayCalendarAssignment:
    id: int
    employee_id: int
    matricula: str
    holiday_calendar_id: int

    holiday_calendar: "HolidayCalendar"

    def __init__(self, employee_id: int, matricula: str, holiday_calendar_id: int):
        self.employee_id = employee_id
        self.matricula = matricula
        self.holiday_calendar_id = holiday_calendar_id
