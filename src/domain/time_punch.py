from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from .enums import PunchType

if TYPE_CHECKING:  # pragma: no cover
    from .employee_enrollment import EmployeeEnrollment
    from .time_adjustment_item import TimeAdjustmentItem


class TimePunch:
    id: int
    tenant_id: int
    enrollment_id: int
    punched_at: datetime
    punch_type: PunchType
    source: str
    note: Optional[str]

    enrollment: "EmployeeEnrollment"
    adjustment_items: List["TimeAdjustmentItem"]

    def __init__(
        self,
        tenant_id: int,
        enrollment_id: int,
        punched_at: datetime,
        punch_type: PunchType,
        source: str = "web",
        note: Optional[str] = None,
    ):
        self.tenant_id = tenant_id
        self.enrollment_id = enrollment_id
        self.punched_at = punched_at
        self.punch_type = punch_type
        self.source = source
        self.note = note
        self.adjustment_items = []
