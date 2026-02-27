from dataclasses import dataclass
from typing import Optional


@dataclass
class ListHolidayCalendarsDTO:
    page: int
    per_page: int
    tenant_id: Optional[int] = None
    name: Optional[str] = None
    city: Optional[str] = None
    uf: Optional[str] = None
