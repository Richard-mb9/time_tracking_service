from dataclasses import dataclass
from typing import List, Optional

from .holiday_dto import HolidayDTO


@dataclass
class UpdateHolidayCalendarDTO:
    name: Optional[str] = None
    city: Optional[str] = None
    uf: Optional[str] = None
    holidays: Optional[List[HolidayDTO]] = None
