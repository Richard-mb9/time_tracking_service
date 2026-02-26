from dataclasses import dataclass
from typing import Optional

from domain.enums import TimeAdjustmentStatus


@dataclass
class DecideTimeAdjustmentRequestDTO:
    status: TimeAdjustmentStatus
    decided_by_user_id: int
    decision_reason: Optional[str] = None
