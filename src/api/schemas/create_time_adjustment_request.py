from datetime import date
from typing import List

from pydantic import BaseModel

from .create_time_adjustment_item_request import CreateTimeAdjustmentItemRequest
from .enums import TimeAdjustmentTypeRequestEnum


class CreateTimeAdjustmentRequest(BaseModel):
    tenantId: int
    employeeId: int
    matricula: str
    requestDate: date
    requestType: TimeAdjustmentTypeRequestEnum
    reason: str
    requesterUserId: int
    items: List[CreateTimeAdjustmentItemRequest]
