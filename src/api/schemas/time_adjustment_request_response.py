from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional

from .time_adjustment_item_response import TimeAdjustmentItemResponse


@dataclass
class TimeAdjustmentRequestResponse:
    id: int
    tenantId: int
    enrollmentId: int
    requestDate: date
    requestType: str
    status: str
    reason: str
    requesterUserId: int
    decidedAt: Optional[datetime]
    decidedByUserId: Optional[int]
    decisionReason: Optional[str]
    items: List[TimeAdjustmentItemResponse] = field(default_factory=list)
