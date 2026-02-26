from dataclasses import dataclass, field
from datetime import date
from typing import List

from domain.enums import TimeAdjustmentType

from .create_time_adjustment_item_dto import CreateTimeAdjustmentItemDTO


@dataclass
class CreateTimeAdjustmentRequestDTO:
    tenant_id: int
    enrollment_id: int
    request_date: date
    request_type: TimeAdjustmentType
    reason: str
    requester_user_id: int
    items: List[CreateTimeAdjustmentItemDTO] = field(default_factory=list)
