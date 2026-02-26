from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TimePunchResponse:
    id: int
    tenantId: int
    enrollmentId: int
    punchedAt: datetime
    punchType: str
    source: str
    note: Optional[str]
