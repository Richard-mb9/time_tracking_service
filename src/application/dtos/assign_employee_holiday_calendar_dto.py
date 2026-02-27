from dataclasses import dataclass


@dataclass
class AssignEmployeeHolidayCalendarDTO:
    tenant_id: int
    employee_id: int
    holiday_calendar_id: int
