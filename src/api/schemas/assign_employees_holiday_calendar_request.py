from typing import List

from pydantic import BaseModel


class AssignEmployeesHolidayCalendarItemRequest(BaseModel):
    employeeId: int
    matricula: str


class AssignEmployeesHolidayCalendarRequest(BaseModel):
    employees: List[AssignEmployeesHolidayCalendarItemRequest]
