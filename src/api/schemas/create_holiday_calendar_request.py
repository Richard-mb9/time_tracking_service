from datetime import date
from typing import List, Optional

from pydantic import BaseModel

from .enums import UfRequestEnum
from .holiday_request import HolidayRequest


class CreateHolidayCalendarRequest(BaseModel):
    tenantId: int
    name: str
    effectiveFrom: date
    effectiveTo: date
    national: bool = False
    city: Optional[str] = None
    uf: Optional[UfRequestEnum] = None
    holidays: List[HolidayRequest]
