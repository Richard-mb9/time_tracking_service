from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from .holiday_dto import HolidayDTO


@dataclass
class UpdateHolidayCalendarDTO:
    name: Optional[str] = None
    city: Optional[str] = None
    uf: Optional[str] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    national: Optional[bool] = None
    holidays: Optional[List[HolidayDTO]] = None
