from typing import List, Optional

from pydantic import BaseModel

from .enums import UfRequestEnum
from .holiday_request import HolidayRequest


class UpdateHolidayCalendarRequest(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    uf: Optional[UfRequestEnum] = None
    holidays: Optional[List[HolidayRequest]] = None
