from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TimeAdjustmentItemResponse:
    id: int
    requestId: int
    proposedPunchType: Optional[str]
    proposedPunchedAt: Optional[datetime]
    originalPunchId: Optional[int]
    note: Optional[str]
