from datetime import date
from typing import List, Optional

from pydantic import BaseModel

from .enums import UfRequestEnum
from .holiday_request import HolidayRequest


class UpdateHolidayCalendarRequest(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    uf: Optional[UfRequestEnum] = None
    effectiveFrom: Optional[date] = None
    effectiveTo: Optional[date] = None
    national: Optional[bool] = None
    holidays: Optional[List[HolidayRequest]] = None
