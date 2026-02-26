from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class BankHoursLedgerResponse:
    id: int
    tenantId: int
    enrollmentId: int
    eventDate: date
    minutesDelta: int
    source: str
    referenceId: Optional[int]
