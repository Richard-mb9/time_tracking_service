from dataclasses import dataclass


@dataclass
class EmployeeHolidayCalendarAssignmentResponse:
    id: int
    employeeId: int
    holidayCalendarId: int
