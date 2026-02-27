from dataclasses import dataclass


@dataclass
class AssignEmployeeHolidayCalendarDTO:
    tenant_id: int
    employee_id: int
    matricula: str
    holiday_calendar_id: int
