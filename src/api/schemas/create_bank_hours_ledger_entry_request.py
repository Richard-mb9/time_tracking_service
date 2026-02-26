from datetime import date
from typing import Optional

from pydantic import BaseModel

from .enums import BankHoursSourceRequestEnum


class CreateBankHoursLedgerEntryRequest(BaseModel):
    tenantId: int
    employeeId: int
    matricula: str
    eventDate: date
    minutesDelta: int
    source: BankHoursSourceRequestEnum
    referenceId: Optional[int] = None
