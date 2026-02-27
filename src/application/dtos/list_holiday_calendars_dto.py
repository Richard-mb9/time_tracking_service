from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class ListHolidayCalendarsDTO:
    page: int
    per_page: int
    tenant_id: Optional[int] = None
    name: Optional[str] = None
    city: Optional[str] = None
    uf: Optional[str] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    national: Optional[bool] = None
