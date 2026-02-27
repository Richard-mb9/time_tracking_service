from dataclasses import dataclass, field
from datetime import date
from typing import List


@dataclass
class HolidayResponse:
    id: int
    date: date
    name: str


@dataclass
class HolidayCalendarResponse:
    id: int
    tenantId: int
    name: str
    city: str
    uf: str
    holidays: List[HolidayResponse] = field(default_factory=list)
