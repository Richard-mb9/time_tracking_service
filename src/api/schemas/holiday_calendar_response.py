from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional


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
    effectiveFrom: date
    effectiveTo: date
    national: bool
    city: Optional[str]
    uf: Optional[str]
    holidays: List[HolidayResponse] = field(default_factory=list)
