from datetime import date
from typing import Optional

from .enums import BankHoursSource


class BankHoursLedger:
    id: int
    tenant_id: int
    employee_id: int
    matricula: str
    event_date: date
    minutes_delta: int
    source: BankHoursSource
    reference_id: Optional[int]

    def __init__(
        self,
        tenant_id: int,
        employee_id: int,
        matricula: str,
        event_date: date,
        minutes_delta: int,
        source: BankHoursSource,
        reference_id: Optional[int] = None,
    ):
        self.tenant_id = tenant_id
        self.employee_id = employee_id
        self.matricula = matricula
        self.event_date = event_date
        self.minutes_delta = minutes_delta
        self.source = source
        self.reference_id = reference_id
