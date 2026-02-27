from typing import List

from pydantic import BaseModel

from .enums import UfRequestEnum
from .holiday_request import HolidayRequest


class CreateHolidayCalendarRequest(BaseModel):
    tenantId: int
    name: str
    city: str
    uf: UfRequestEnum
    holidays: List[HolidayRequest]
