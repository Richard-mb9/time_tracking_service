from datetime import datetime
from typing import Optional, TYPE_CHECKING

from .enums import PunchType

if TYPE_CHECKING:  # pragma: no cover
    from .time_adjustment_request import TimeAdjustmentRequest
    from .time_punch import TimePunch


class TimeAdjustmentItem:
    id: int
    tenant_id: int
    request_id: int
    proposed_punch_type: Optional[PunchType]
    proposed_punched_at: Optional[datetime]
    original_punch_id: Optional[int]
    note: Optional[str]

    request: "TimeAdjustmentRequest"
    original_punch: Optional["TimePunch"]

    def __init__(
        self,
        tenant_id: int,
        request_id: int,
        proposed_punch_type: Optional[PunchType] = None,
        proposed_punched_at: Optional[datetime] = None,
        original_punch_id: Optional[int] = None,
        note: Optional[str] = None,
    ):
        self.tenant_id = tenant_id
        self.request_id = request_id
        self.proposed_punch_type = proposed_punch_type
        self.proposed_punched_at = proposed_punched_at
        self.original_punch_id = original_punch_id
        self.note = note
