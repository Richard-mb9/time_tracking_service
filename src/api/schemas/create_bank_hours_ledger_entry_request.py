from datetime import date
from typing import Optional

from pydantic import BaseModel

from .enums import BankHoursSourceRequestEnum


class CreateBankHoursLedgerEntryRequest(BaseModel):
    tenantId: int
    enrollmentId: int
    eventDate: date
    minutesDelta: int
    source: BankHoursSourceRequestEnum
    referenceId: Optional[int] = None
