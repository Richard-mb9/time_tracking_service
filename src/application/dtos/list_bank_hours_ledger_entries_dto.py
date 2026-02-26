from dataclasses import dataclass
from datetime import date
from typing import Optional

from domain.enums import BankHoursSource


@dataclass
class ListBankHoursLedgerEntriesDTO:
    page: int
    per_page: int
    tenant_id: Optional[int] = None
    enrollment_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    source: Optional[BankHoursSource] = None
