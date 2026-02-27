from pydantic import BaseModel

from .enums import WorkWeekDayRequestEnum


class WorkDayPolicyRequest(BaseModel):
    weekDay: WorkWeekDayRequestEnum
    dailyWorkMinutes: int
    breakMinutes: int
