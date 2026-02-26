from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class BankHoursLedgerResponse:
    id: int
    tenantId: int
    employeeId: int
    matricula: str
    eventDate: date
    minutesDelta: int
    source: str
    referenceId: Optional[int]
