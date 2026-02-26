from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TimePunchResponse:
    id: int
    tenantId: int
    employeeId: int
    matricula: str
    punchedAt: datetime
    punchType: str
    source: str
    note: Optional[str]
