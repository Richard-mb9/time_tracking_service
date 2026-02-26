from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from domain.enums import PunchType


@dataclass
class CreateTimePunchDTO:
    tenant_id: int
    employee_id: int
    matricula: str
    punched_at: datetime
    punch_type: PunchType
    source: str = "web"
    note: Optional[str] = None
    allow_multi_enrollment_per_day: bool = True
