from dataclasses import dataclass


@dataclass
class EmployeeHolidayCalendarAssignmentResponse:
    id: int
    employeeId: int
    matricula: str
    holidayCalendarId: int
