from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from domain.enums import PunchType


@dataclass
class ListTimePunchesDTO:
    page: int
    per_page: int
    tenant_id: Optional[int] = None
    enrollment_id: Optional[int] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    punch_type: Optional[PunchType] = None
