from dataclasses import dataclass
from datetime import date


@dataclass
class GetBankHoursBalanceDTO:
    employee_id: int
    matricula: str
    until_date: date
