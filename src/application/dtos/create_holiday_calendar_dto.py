from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from .holiday_dto import HolidayDTO


@dataclass
class CreateHolidayCalendarDTO:
    tenant_id: int
    name: str
    effective_from: date
    effective_to: date
    holidays: List[HolidayDTO]
    national: bool = False
    city: Optional[str] = None
    uf: Optional[str] = None
