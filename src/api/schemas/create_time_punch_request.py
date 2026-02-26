from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .enums import PunchTypeRequestEnum


class CreateTimePunchRequest(BaseModel):
    tenantId: int
    employeeId: int
    matricula: str
    punchedAt: datetime
    punchType: PunchTypeRequestEnum
    source: str = "web"
    note: Optional[str] = None
    allowMultiEnrollmentPerDay: bool = True
