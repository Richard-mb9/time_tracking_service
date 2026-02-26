from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from domain.enums import PunchType


@dataclass
class CreateTimeAdjustmentItemDTO:
    proposed_punch_type: Optional[PunchType] = None
    proposed_punched_at: Optional[datetime] = None
    original_punch_id: Optional[int] = None
    note: Optional[str] = None
