from dataclasses import dataclass
from datetime import date


@dataclass
class BankHoursBalanceResponse:
    enrollmentId: int
    untilDate: date
    balanceMinutes: int
