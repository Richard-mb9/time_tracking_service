from datetime import date, datetime
from typing import List, Optional, TYPE_CHECKING

from .enums import TimeAdjustmentStatus, TimeAdjustmentType

if TYPE_CHECKING:  # pragma: no cover
    from .employee_enrollment import EmployeeEnrollment
    from .time_adjustment_item import TimeAdjustmentItem


class TimeAdjustmentRequest:
    id: int
    tenant_id: int
    enrollment_id: int
    request_date: date
    request_type: TimeAdjustmentType
    status: TimeAdjustmentStatus
    reason: str
    requester_user_id: int
    decided_at: Optional[datetime]
    decided_by_user_id: Optional[int]
    decision_reason: Optional[str]

    enrollment: "EmployeeEnrollment"
    items: List["TimeAdjustmentItem"]

    def __init__(
        self,
        tenant_id: int,
        enrollment_id: int,
        request_date: date,
        request_type: TimeAdjustmentType,
        reason: str,
        requester_user_id: int,
        status: TimeAdjustmentStatus = TimeAdjustmentStatus.PENDING,
        decided_at: Optional[datetime] = None,
        decided_by_user_id: Optional[int] = None,
        decision_reason: Optional[str] = None,
    ):
        self.tenant_id = tenant_id
        self.enrollment_id = enrollment_id
        self.request_date = request_date
        self.request_type = request_type
        self.status = status
        self.reason = reason
        self.requester_user_id = requester_user_id
        self.decided_at = decided_at
        self.decided_by_user_id = decided_by_user_id
        self.decision_reason = decision_reason
        self.items = []
