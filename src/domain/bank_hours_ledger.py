from datetime import date
from typing import Optional, TYPE_CHECKING

from .enums import BankHoursSource

if TYPE_CHECKING:  # pragma: no cover
    from .employee_enrollment import EmployeeEnrollment


class BankHoursLedger:
    id: int
    tenant_id: int
    enrollment_id: int
    event_date: date
    minutes_delta: int
    source: BankHoursSource
    reference_id: Optional[int]

    enrollment: "EmployeeEnrollment"

    def __init__(
        self,
        tenant_id: int,
        enrollment_id: int,
        event_date: date,
        minutes_delta: int,
        source: BankHoursSource,
        reference_id: Optional[int] = None,
    ):
        self.tenant_id = tenant_id
        self.enrollment_id = enrollment_id
        self.event_date = event_date
        self.minutes_delta = minutes_delta
        self.source = source
        self.reference_id = reference_id
