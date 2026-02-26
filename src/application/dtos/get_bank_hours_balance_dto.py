from dataclasses import dataclass
from datetime import date


@dataclass
class GetBankHoursBalanceDTO:
    enrollment_id: int
    until_date: date
