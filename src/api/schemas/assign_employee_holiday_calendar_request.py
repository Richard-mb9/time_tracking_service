from pydantic import BaseModel


class AssignEmployeeHolidayCalendarRequest(BaseModel):
    holidayCalendarId: int
