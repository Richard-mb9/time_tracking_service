from dataclasses import dataclass
from typing import List


@dataclass
class AssignEmployeesHolidayCalendarItemDTO:
    employee_id: int
    matricula: str


@dataclass
class AssignEmployeesHolidayCalendarDTO:
    tenant_id: int
    holiday_calendar_id: int
    employees: List[AssignEmployeesHolidayCalendarItemDTO]
