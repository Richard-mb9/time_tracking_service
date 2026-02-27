from dataclasses import dataclass
from typing import List

from .holiday_dto import HolidayDTO


@dataclass
class CreateHolidayCalendarDTO:
    tenant_id: int
    name: str
    city: str
    uf: str
    holidays: List[HolidayDTO]
