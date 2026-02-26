from dataclasses import dataclass
from datetime import date
from typing import Optional

from domain.enums import BankHoursSource


@dataclass
class CreateBankHoursLedgerEntryDTO:
    tenant_id: int
    enrollment_id: int
    event_date: date
    minutes_delta: int
    source: BankHoursSource
    reference_id: Optional[int] = None
