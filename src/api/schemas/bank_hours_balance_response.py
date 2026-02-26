from dataclasses import dataclass
from datetime import date


@dataclass
class BankHoursBalanceResponse:
    employeeId: int
    matricula: str
    untilDate: date
    balanceMinutes: int
