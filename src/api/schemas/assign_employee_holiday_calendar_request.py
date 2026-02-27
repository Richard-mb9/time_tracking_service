from pydantic import BaseModel


class AssignEmployeeHolidayCalendarRequest(BaseModel):
    matricula: str
    holidayCalendarId: int
