from typing import Optional

from pydantic import BaseModel

from .enums import TimeAdjustmentDecisionStatusRequestEnum


class DecideTimeAdjustmentRequest(BaseModel):
    status: TimeAdjustmentDecisionStatusRequestEnum
    decidedByUserId: int
    decisionReason: Optional[str] = None
